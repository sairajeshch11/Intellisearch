import json
import os
import re
from collections import defaultdict
import math
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DOCS_PATH = BASE_DIR / "data" / "docs_2000.jsonl"
OUT_DIR = (BASE_DIR / ".." / "output").resolve()
OUT_DIR.mkdir(parents=True, exist_ok=True)


os.makedirs(OUT_DIR, exist_ok=True)

def tokenize(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return text.split()


docs = {}         # doc_id -> raw text
cleaned_docs = {} # doc_id -> tokens

print(f"Loading {DOCS_PATH} ...")

with open(DOCS_PATH, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        entry = json.loads(line)

        doc_id = entry.get("id") or entry.get("doc_id") or entry.get("_id")
        text = entry.get("text") or (entry.get("title", "") + " " + entry.get("abstract", ""))

        if doc_id is None:
            # fallback if no id field exists
            doc_id = str(len(docs))

        docs[doc_id] = text
        cleaned_docs[doc_id] = tokenize(text)

print(f"Loaded {len(docs)} documents.")


# ----------------------------------------
# BUILD INDEXES
# ----------------------------------------
positional_index = defaultdict(lambda: defaultdict(list))
biword_index = defaultdict(list)

print("Building positional + biword indexes ...")

for doc_id, tokens in cleaned_docs.items():
    # positional index
    for pos, term in enumerate(tokens):
        positional_index[term][doc_id].append(pos)

    # biword index
    for i in range(len(tokens) - 1):
        pair = tokens[i] + " " + tokens[i + 1]
        biword_index[pair].append(doc_id)

# convert defaultdict to normal dict for saving
positional_index = {t: dict(v) for t, v in positional_index.items()}
biword_index = dict(biword_index)

# ----------------------------------------
# COMPUTE IDF
# ----------------------------------------
print("Computing IDF ...")

N = len(cleaned_docs)
df = defaultdict(int)

for doc_tokens in cleaned_docs.values():
    unique_terms = set(doc_tokens)
    for t in unique_terms:
        df[t] += 1

idf = {t: math.log((N + 1) / (df_val + 1)) + 1 for t, df_val in df.items()}

# ----------------------------------------
# SAVE OUTPUT FILES
# ----------------------------------------
print("Saving index files ...")

with open(OUT_DIR / "positional_index.json", "w", encoding="utf-8") as f:
    json.dump(positional_index, f)

with open(OUT_DIR / "biword_index.json", "w", encoding="utf-8") as f:
    json.dump(biword_index, f)

with open(OUT_DIR / "idf.json", "w", encoding="utf-8") as f:
    json.dump(idf, f)


print("DONE! Indexes saved successfully.")

