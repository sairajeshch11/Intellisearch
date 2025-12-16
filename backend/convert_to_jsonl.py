import os
import json

RAW_DIR = r"C:/Projects/HybridSearchEngine/data/raw_docs"
OUT_FILE = r"C:/Projects/HybridSearchEngine/data/docs.jsonl"

with open(OUT_FILE, "w", encoding="utf-8") as out:
    for file in os.listdir(RAW_DIR):
        if not file.endswith(".txt"):
            continue
        doc_id = file.replace(".txt", "")
        with open(os.path.join(RAW_DIR, file), "r", encoding="utf-8") as f:
            text = f.read()

        entry = {"id": doc_id, "text": text}
        out.write(json.dumps(entry) + "\n")

print("DONE: docs.jsonl created")
