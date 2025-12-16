import os, json
from tqdm import tqdm

RAW_DIR = "C:/Projects/HybridSearchEngine/data/raw_docs"
CLEAN_DIR = "C:/Projects/HybridSearchEngine/data/cleaned_docs"
OUT_DIR = "C:/Projects/HybridSearchEngine/output"

os.makedirs(OUT_DIR, exist_ok=True)

docs = {}
cleaned_docs = {}

print("📦 Loading and combining documents...")
for file in tqdm(os.listdir(RAW_DIR)):
    if not file.endswith(".txt"):
        continue
    doc_id = file.replace(".txt", "")
    with open(os.path.join(RAW_DIR, file), "r", encoding="utf-8") as f:
        docs[doc_id] = f.read()

for file in tqdm(os.listdir(CLEAN_DIR)):
    if not file.endswith(".txt"):
        continue
    doc_id = file.replace(".txt", "")
    with open(os.path.join(CLEAN_DIR, file), "r", encoding="utf-8") as f:
        cleaned_docs[doc_id] = f.read().split()

with open(os.path.join(OUT_DIR, "all_docs.json"), "w", encoding="utf-8") as f:
    json.dump(docs, f)

with open(os.path.join(OUT_DIR, "cleaned_docs.json"), "w", encoding="utf-8") as f:
    json.dump(cleaned_docs, f)

print("✅ Saved combined JSON files:")
print(f"📄 all_docs.json and cleaned_docs.json in {OUT_DIR}")
