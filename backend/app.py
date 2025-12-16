import tokenize
import streamlit as st
import json
from collections import Counter
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DOCS_PATH = BASE_DIR / "data" / "docs_2000.jsonl"     # backend/data/docs_2000.jsonl
INDEX_DIR = (BASE_DIR / ".." / "output").resolve()    # output/


DARK_CSS = """
<style>
.stApp { background-color: #111418; color: #e6e6e6; font-family: "Inter", sans-serif; }
h1, h2, h3 { color: #8ab4f8; }

/* Result cards */
.result-card { 
    background-color: #1c1f24; 
    padding: 1.3rem; 
    border-radius: 12px; 
    margin-bottom: 1.2rem; 
    border: 1px solid #2b3138; 
}
.result-title { color: #8ab4f8; font-size: 20px; font-weight: 600; }
.result-meta { color: #b5b5b5; font-size: 13px; }
.result-snippet { font-size: 14px; margin-top: 10px; }

/* Buttons / links */
.pdf-btn { 
    background-color: #3d80d0; 
    color: white !important; 
    padding: 6px 12px; 
    border-radius: 6px; 
    font-size: 13px; 
    text-decoration: none;
}
.small-link { 
    color: #8ab4f8; 
    font-size: 12px; 
    margin-right: 12px; 
    text-decoration: none;
}
.small-link:hover { text-decoration: underline; }

/* Tags (if you add later) */
.tag { 
    background-color:#3a3f44; 
    padding:4px 8px; 
    margin-right:5px; 
    border-radius:6px; 
    font-size:12px; 
    color:#9cc9ff; 
}
/* Fix button alignment */
.button-full { width: 80%; }
 
/* Remove white outline everywhere */
*:focus {
    outline: none !important;
    box-shadow: none !important;
}
/* REMOVE ALL STREAMLIT FOCUS OUTLINES PROPERLY */
div:focus, span:focus, section:focus, button:focus,
input:focus, textarea:focus, label:focus, 
[data-testid]:focus, .stColumn:focus, .stButton>button:focus {
    outline: none !important;
    box-shadow: none !important;
}


/* Stretch and style search button */
.stButton > button {
    width: 30% !important;
    height: 46px !important;
    border-radius: 8px !important;
    background-color: #3d80d0 !important;
    color: white !important;
    font-size: 16px !important;
}

/* --- Add this block at the bottom --- */

input[type="text"],
textarea,
div[contenteditable="true"],
.stTextInput input,
.stTextArea textarea {
    caret-color: transparent !important;
    color: #e6e6e6 !important;
}

input:focus,
textarea:focus,
.stTextInput input:focus,
.stTextArea textarea:focus,
button:focus,
[data-testid]:focus {
    outline: none !important;
    box-shadow: none !important;
}

h1,h2,h3,h4,h5,h6
{caret-color:transparent !important}
</style>
"""

# ----------------------------- LOAD INDEXES -----------------------------
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INDEX_DIR = (BASE_DIR / ".." / "output").resolve()

@st.cache_resource
def load_indexes():
    # DEBUG LINES — PUT THEM HERE
    st.sidebar.write(f"INDEX_DIR: {INDEX_DIR}")
    st.sidebar.write(f"Index exists? {(INDEX_DIR / 'positional_index.json').exists()}")

    # NOW load the files
    with open(INDEX_DIR / "positional_index.json", "r", encoding="utf-8") as f:
        pos_index = json.load(f)

    with open(INDEX_DIR / "biword_index.json", "r", encoding="utf-8") as f:
        bi_index = json.load(f)

    with open(INDEX_DIR / "idf.json", "r", encoding="utf-8") as f:
        idf = json.load(f)

    return pos_index, bi_index, idf


# ------------------------- LOAD DOCUMENTS -------------------------
@st.cache_resource
def load_docs():
    st.sidebar.write(f"DOCS_PATH: {DOCS_PATH}")
    st.sidebar.write(f"Docs exists? {DOCS_PATH.exists()}")

    docs = {}
    cleaned_docs = {}

    with open(DOCS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            entry = json.loads(line)
            doc_id = entry.get("id") or entry.get("doc_id") or entry.get("_id") or str(len(docs))
            text = entry.get("text") or (entry.get("title", "") + " " + entry.get("abstract", ""))
            docs[doc_id] = text
            cleaned_docs[doc_id] = tokenize(text)

    return docs, cleaned_docs


# ------------------------- HELPERS -------------------------
def intersect(a, b):
    i = j = 0
    res = []
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            res.append(a[i]); i += 1; j += 1
        elif a[i] < b[j]:
            i += 1
        else:
            j += 1
    return res

def boolean_and(t1, t2, pos_index):
    return intersect(sorted(pos_index.get(t1, {}).keys()),
                     sorted(pos_index.get(t2, {}).keys()))

def phrase_query(phrase, bi_index, pos_index):
    tokens = phrase.lower().split()
    if len(tokens) == 1:
        return sorted(pos_index.get(tokens[0], {}).keys())

    biwords = [" ".join(tokens[i:i+2]) for i in range(len(tokens)-1)]
    postings = [bi_index.get(b, []) for b in biwords if b in bi_index]

    if not postings:
        return []

    result = postings[0]
    for p in postings[1:]:
        result = intersect(result, p)

    return result

def proximity_query(t1, t2, k, pos_index):
    docs = set(pos_index.get(t1, {})) & set(pos_index.get(t2, {}))
    out = []
    for d in docs:
        for p1 in pos_index[t1][d]:
            for p2 in pos_index[t2][d]:
                if abs(p1 - p2) <= k:
                    out.append(d)
                    break
            else:
                continue
            break
    return out

def bm25_score(tokens, filtered_docs, idf, k1=1.5, b=0.75):
    if not filtered_docs:
        return []

    avg_len = sum(len(v) for v in filtered_docs.values()) / len(filtered_docs)
    scores = {}

    for doc_id, words in filtered_docs.items():
        tf = Counter(words)
        score = 0
        for q in tokens:
            if q in tf and q in idf:
                freq = tf[q]
                score += idf[q] * freq * (k1 + 1) / \
                         (freq + k1 * (1 - b + b * len(words) / avg_len))

        if score > 0:
            scores[doc_id] = round(score, 4)

    return sorted(scores.items(), key=lambda x: x[1], reverse=True)

def highlight_terms(text, terms):
    for t in terms:
        text = text.replace(t, f"<span style='color:#61dafb; font-weight:bold;'>{t}</span>")
    return text

def cached_search(query, qtype, k, pos_index, bi_index, cleaned_docs, idf):
    key = f"{qtype}|{query}|{k}"

    if key in st.session_state.cache:
        return st.session_state.cache[key]

    q = query.lower().split()

    if qtype == "Boolean (AND)" and len(q) == 2:
        docs = boolean_and(q[0], q[1], pos_index)

    elif qtype == "Phrase":
        docs = phrase_query(query, bi_index, pos_index)

    elif qtype == "Proximity" and len(q) == 2:
        docs = proximity_query(q[0], q[1], k, pos_index)

    else:
        docs = []

    filtered = {d: cleaned_docs[d] for d in docs if d in cleaned_docs}
    ranked = bm25_score(q, filtered, idf)
    st.session_state.cache[key] = ranked

    return ranked

# ------------------------- MAIN APP -------------------------
def main():
    st.set_page_config(page_title="Hybrid Search Engine", layout="wide")
    st.markdown(DARK_CSS, unsafe_allow_html=True)

    if "cache" not in st.session_state:
        st.session_state.cache = {}

    # --- Sidebar with navigation + about info ---
    with st.sidebar:
        st.markdown("### 📂 Navigation")
        page = st.radio("Go to", ["🔍 Search", "👤 About the App"])

    # ========== ABOUT PAGE ==========
    if page == "👤 About the App":
        st.title("👤 About IntelliSearch")

        col1, col2 = st.columns([1, 2])
        with col1:
            # Put your photo at this path
            photo_path = "C:/Projects/HybridSearchEngine/backend/profile.jpg"
            try:
                st.image(photo_path)
            except Exception:
                st.write("Add your photo file here:")
                st.code(photo_path)

        with col2:
            st.subheader("Kameswari Dwaraka Sai Lakshmi Peri")
            st.markdown(
                """
**Graduate Student — M.S. in Computer Science**  
*University of South Dakota*  

This project is a **Hybrid Academic Search Engine** built for the  
*Information Storage & Retrieval* course.  

IntelliSearch is a Hybrid Academic Search Engine designed to explore how
Information Retrieval systems work behind the scenes.  
This application integrates traditional IR models such as Boolean, Phrase,
and Proximity search with modern ranking techniques like BM25.

The goal of this project is to demonstrate how large text collections can be
indexed, queried, filtered, and ranked efficiently — similar to how real
scholarly platforms like Google Scholar operate.


**Key Features:**
- Boolean (AND) search  
- Phrase search  
- Proximity search  
- BM25 ranked retrieval over arXiv-style abstracts  
- Dark scholarly UI inspired by Google Scholar
                """
            )

        st.markdown("---")
        st.markdown("Use the sidebar to switch back to **🔍 Search**.")
        return  # stop here when on About page

    st.title("🎓 IntelliSearch — Hybrid Academic Paper Search")

    st.markdown("### 🔍 Search")
    query = st.text_input("",placeholder="Enter your query:")

    col1, col2, col3 = st.columns(3)
    with col1:
        qtype = st.selectbox("Query Type", ["Boolean (AND)", "Phrase", "Proximity"])
    with col2:
        k = st.number_input("Proximity Window (k)", 1, 10, 3)
    with col3:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)  # pushes button down
    do_search = st.button("🚀 Search", use_container_width=True)

    pos_index, bi_index, idf = load_indexes()
    docs, cleaned_docs = load_docs()

    if do_search:

        if not query.strip():
            st.warning("Please enter a valid query.")
            return

        with st.spinner("🔎 Searching..."):
            ranked = cached_search(query, qtype, k, pos_index, bi_index, cleaned_docs, idf)

        if not ranked:
            st.error("No matching documents found.")
            return

        st.success(f"Found {len(ranked)} results")

        st.markdown("### 📄 Top Results")

        query_tokens = query.lower().split()

        for doc, score in ranked[:10]:
            raw = docs.get(doc, "")
            title = doc.replace("_", " ").title()
            snippet = " ".join(raw.split()[:90]) + "..."
            snippet_html = highlight_terms(snippet, query_tokens)

            pdf_link = "#"

            html = f"""
            <div class='result-card'>
                <div class='result-title'>{title}</div>
                <div class='result-meta'>Score: <b>{score:.4f}</b></div>
                <div class='result-snippet'>{snippet_html}</div>
                <div style='margin-top:12px;'>
                    <a class='pdf-btn' href='{pdf_link}'>📄 View PDF</a>
                    <a class='small-link' href='#'>Cite</a>
                    <a class='small-link' href='#'>Related</a>
                </div>
            </div>
            """

            st.markdown(html, unsafe_allow_html=True)


if __name__ == "__main__":
    main()

