import json
import os

# Paths to index files
positional_path = "C:\Projects\HybridSearchEngine\output/positional_index.json"
biword_path = "C:\Projects\HybridSearchEngine\output/biword_index.json"

# Utility: Intersect two posting lists
def intersect(list1, list2):
    i, j = 0, 0
    result = []
    while i < len(list1) and j < len(list2):
        if list1[i] == list2[j]:
            result.append(list1[i])
            i += 1
            j += 1
        elif list1[i] < list2[j]:
            i += 1
        else:
            j += 1
    return result

# Load Indexes
def load_indexes():
    with open(positional_path, "r", encoding="utf-8") as f:
        pos_index = json.load(f)
    with open(biword_path, "r", encoding="utf-8") as f:
        bi_index = json.load(f)
    return pos_index, bi_index

# Boolean AND query 
def boolean_and(term1, term2, pos_index):
    docs1 = sorted(pos_index.get(term1, {}).keys())
    docs2 = sorted(pos_index.get(term2, {}).keys())
    return intersect(docs1, docs2)

#  Phrase query 
def phrase_query(phrase, bi_index, pos_index):
    tokens = phrase.lower().split()
    if len(tokens) == 1:
        return sorted(pos_index.get(tokens[0], {}).keys())

    # create list of biwords
    biwords = [" ".join(tokens[i:i+2]) for i in range(len(tokens)-1)]
    # start intersection
    postings = [bi_index.get(b, []) for b in biwords if b in bi_index]
    if not postings:
        return []

    result = postings[0]
    for p in postings[1:]:
        result = intersect(result, p)
    if not result:
        return []

    # verify actual positions using positional index
    verified_docs = []
    for doc in result:
        first_term_positions = pos_index.get(tokens[0], {}).get(doc, [])
        for pos in first_term_positions:
            match = True
            for i in range(1, len(tokens)):
                term_positions = pos_index.get(tokens[i], {}).get(doc, [])
                if (pos + i) not in term_positions:
                    match = False
                    break
            if match:
                verified_docs.append(doc)
                break
    return sorted(verified_docs)

# Proximity query
def proximity_query(term1, term2, k, pos_index):
    docs1 = set(pos_index.get(term1, {}).keys())
    docs2 = set(pos_index.get(term2, {}).keys())
    common_docs = docs1.intersection(docs2)
    results = []

    for doc in common_docs:
        positions1 = pos_index[term1][doc]
        positions2 = pos_index[term2][doc]
        for p1 in positions1:
            for p2 in positions2:
                if abs(p1 - p2) <= k:
                    results.append(doc)
                    break
            else:
                continue
            break
    return sorted(results)

# MAIN INTERFACE 
def main():
    pos_index, bi_index = load_indexes()
    print("✅ Indexes loaded successfully!\n")

    while True:
        print("\n🔎 Choose query type:")
        print("1. Boolean AND query")
        print("2. Phrase query")
        print("3. Proximity query")
        print("4. Exit")
        choice = input("Enter your choice (1/2/3/4): ").strip()

        if choice == "1":
            t1 = input("Enter first term: ").strip().lower()
            t2 = input("Enter second term: ").strip().lower()
            results = boolean_and(t1, t2, pos_index)
            print(f"→ Found {len(results)} matching docs:", results)

        elif choice == "2":
            phrase = input("Enter phrase (use quotes optional): ").strip().lower()
            results = phrase_query(phrase, bi_index, pos_index)
            print(f"→ Found {len(results)} matching docs:", results)

        elif choice == "3":
            t1 = input("Enter first term: ").strip().lower()
            t2 = input("Enter second term: ").strip().lower()
            k = int(input("Enter proximity (k): ").strip())
            results = proximity_query(t1, t2, k, pos_index)
            print(f"→ Found {len(results)} matching docs:", results)

        elif choice == "4":
            print("👋 Exiting...")
            break
        else:
            print("Invalid choice. Try again!")

if __name__ == "__main__":
    main()
