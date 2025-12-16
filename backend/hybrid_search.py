import json
import os
import math
from collections import Counter, defaultdict

# Load Indexes 
def load_indexes():
    with open("C:\Projects\HybridSearchEngine\output/positional_index.json", "r", encoding="utf-8") as f:
        pos_index = json.load(f)
    with open("C:\Projects\HybridSearchEngine\output/biword_index.json", "r", encoding="utf-8") as f:
        bi_index = json.load(f)
    return pos_index, bi_index

# Load Cleaned Docs 
def load_docs():
    docs = {}
    path = "C:\Projects\HybridSearchEngine\data/cleaned_docs"
    for file in os.listdir(path):
        if file.endswith(".txt"):
            with open(os.path.join(path, file), "r", encoding="utf-8") as f:
                docs[file.replace(".txt", "")] = f.read().split()
    return docs

# Intersection Helper 
def intersect(list1, list2):
    i, j = 0, 0
    res = []
    while i < len(list1) and j < len(list2):
        if list1[i] == list2[j]:
            res.append(list1[i])
            i += 1; j += 1
        elif list1[i] < list2[j]:
            i += 1
        else:
            j += 1
    return res

# Boolean Query
def boolean_and(t1, t2, pos_index):
    docs1 = sorted(pos_index.get(t1, {}).keys())
    docs2 = sorted(pos_index.get(t2, {}).keys())
    return intersect(docs1, docs2)

# Phrase Query 
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
    if not result:
        return []

    verified = []
    for doc in result:
        first_positions = pos_index.get(tokens[0], {}).get(doc, [])
        for p in first_positions:
            match = True
            for i in range(1, len(tokens)):
                positions = pos_index.get(tokens[i], {}).get(doc, [])
                if (p + i) not in positions:
                    match = False
                    break
            if match:
                verified.append(doc)
                break
    return sorted(verified)

# Proximity Query 
def proximity_query(t1, t2, k, pos_index):
    docs1 = set(pos_index.get(t1, {}).keys())
    docs2 = set(pos_index.get(t2, {}).keys())
    common = docs1.intersection(docs2)
    results = []
    for doc in common:
        pos1 = pos_index[t1][doc]
        pos2 = pos_index[t2][doc]
        for p1 in pos1:
            for p2 in pos2:
                if abs(p1 - p2) <= k:
                    results.append(doc)
                    break
            else:
                continue
            break
    return sorted(results)

# TF-IDF + BM25 Ranking
def compute_idf(all_docs):
    N = len(all_docs)
    df = defaultdict(int)
    for tokens in all_docs.values():
        for term in set(tokens):
            df[term] += 1
    return {term: math.log((N + 1) / (df_val + 1)) + 1 for term, df_val in df.items()}

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

# Main Hybrid Search 
def hybrid_search(query_type, query, pos_index, bi_index, docs, idf):
    candidates = []
    if query_type == "boolean":
        t1, t2 = query.split()
        candidates = boolean_and(t1, t2, pos_index)
    elif query_type == "phrase":
        candidates = phrase_query(query, bi_index, pos_index)
    elif query_type == "proximity":
        t1, t2, k = query.split()
        candidates = proximity_query(t1, t2, int(k), pos_index)

    if not candidates:
        print("❌ No matching documents found.")
        return []

    # Rank only retrieved docs
    filtered_docs = {doc: docs[doc] for doc in candidates if doc in docs}
    query_tokens = query.split()
    ranked = bm25_score(query_tokens, filtered_docs, idf)
    return ranked

# MAIN 
def main():
    print("📚 Loading indexes and documents...")
    pos_index, bi_index = load_indexes()
    docs = load_docs()
    idf = compute_idf(docs)
    print(f"✅ Loaded {len(docs)} documents.")

    while True:
        print("\n🔎 Choose search type:")
        print("1. Boolean (AND)")
        print("2. Phrase query")
        print("3. Proximity query")
        print("4. Exit")
        choice = input("Enter choice: ").strip()

        if choice == "1":
            q = input("Enter 2 terms (space separated): ").strip().lower()
            results = hybrid_search("boolean", q, pos_index, bi_index, docs, idf)
        elif choice == "2":
            q = input("Enter phrase: ").strip().lower()
            results = hybrid_search("phrase", q, pos_index, bi_index, docs, idf)
        elif choice == "3":
            q = input("Enter 'term1 term2 k': ").strip().lower()
            results = hybrid_search("proximity", q, pos_index, bi_index, docs, idf)
        elif choice == "4":
            print("👋 Exiting hybrid search.")
            break
        else:
            print("Invalid choice. Try again.")
            continue

        if results:
            print("\nTop Results:")
            for doc, score in results[:10]:
                print(f"{doc}  →  Score: {score}")

if __name__ == "__main__":
    main()
