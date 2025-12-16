import os
import math
from collections import Counter, defaultdict

# Path to cleaned documents
DATA_PATH = "C:\Projects\HybridSearchEngine\data/cleaned_docs"

# TF-IDF RANKING 

def load_docs():
    docs = {}
    for file in os.listdir(DATA_PATH):
        if file.endswith(".txt"):
            with open(os.path.join(DATA_PATH, file), "r", encoding="utf-8") as f:
                docs[file.replace(".txt", "")] = f.read().split()
    return docs

def compute_tf(doc_tokens):
    tf = Counter(doc_tokens)
    total = len(doc_tokens)
    return {term: freq / total for term, freq in tf.items()}

def compute_idf(all_docs):
    N = len(all_docs)
    df = defaultdict(int)
    for tokens in all_docs.values():
        for term in set(tokens):
            df[term] += 1
    return {term: math.log((N + 1) / (df_val + 1)) + 1 for term, df_val in df.items()}

def tfidf_score(query_tokens, docs, idf):
    scores = {}
    for doc_id, tokens in docs.items():
        tf = compute_tf(tokens)
        score = 0.0
        for q in query_tokens:
            if q in tf and q in idf:
                score += tf[q] * idf[q]
        if score > 0:
            scores[doc_id] = round(score, 4)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)

# BM25 RANKING 

def bm25_score(query_tokens, docs, idf, k1=1.5, b=0.75):
    avg_len = sum(len(d) for d in docs.values()) / len(docs)
    scores = {}
    for doc_id, tokens in docs.items():
        tf = Counter(tokens)
        doc_len = len(tokens)
        score = 0.0
        for q in query_tokens:
            if q in tf and q in idf:
                freq = tf[q]
                num = idf[q] * freq * (k1 + 1)
                denom = freq + k1 * (1 - b + b * (doc_len / avg_len))
                score += num / denom
        if score > 0:
            scores[doc_id] = round(score, 4)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)

# ---------- MAIN ----------
def main():
    print("📚 Loading cleaned documents...")
    docs = load_docs()
    print(f"Loaded {len(docs)} docs.")

    idf = compute_idf(docs)

    while True:
        q = input("\nEnter search query (or 'exit'): ").strip().lower()
        if q == "exit":
            break
        query_tokens = q.split()

        print("\nTF-IDF Ranking:")
        tfidf_results = tfidf_score(query_tokens, docs, idf)
        print(tfidf_results[:10])

        print("\nBM25 Ranking:")
        bm25_results = bm25_score(query_tokens, docs, idf)
        print(bm25_results[:10])

if __name__ == "__main__":
    main()
