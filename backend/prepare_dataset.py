import os
import json
import re
from tqdm import tqdm

INPUT_FILE = "C:/Projects/HybridSearchEngine/data/arxiv-metadata-oai-snapshot.json"
RAW_DIR = "C:/Projects/HybridSearchEngine/data/raw_docs"
CLEANED_DIR = "C:/Projects/HybridSearchEngine/data/cleaned_docs"
MAX_DOCS = 20000  # limit to 20K papers

def clean_text(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return text.strip()


if not os.path.exists(RAW_DIR):
    os.makedirs(RAW_DIR)
if not os.path.exists(CLEANED_DIR):
    os.makedirs(CLEANED_DIR)

count = 0
with open(INPUT_FILE, 'r', encoding='utf-8') as infile:
    for line in tqdm(infile, total=2600000, desc="Processing papers"):
        try:
            data = json.loads(line)
            if "categories" in data and "cs" in data["categories"]:  # only Computer Science papers
                title = data.get("title", "")
                abstract = data.get("abstract", "")
                text = f"{title}. {abstract}".strip()

                if not text or len(text.split()) < 30:
                    continue  # skip too short entries

                doc_id = f"doc_{count+1}"
                raw_path = os.path.join(RAW_DIR, f"{doc_id}.txt")
                clean_path = os.path.join(CLEANED_DIR, f"{doc_id}.txt")

                # Save raw
                with open(raw_path, "w", encoding="utf-8") as raw_file:
                    raw_file.write(text)

                # Save cleaned
                cleaned_text = clean_text(text)
                with open(clean_path, "w", encoding="utf-8") as clean_file:
                    clean_file.write(cleaned_text)

                count += 1
                if count >= MAX_DOCS:
                    break
        except Exception as e:
            continue

print(f"\n✅ Completed: {count} Computer Science papers saved.")
print(f"📁 Raw files: {RAW_DIR}")
print(f"📁 Cleaned files: {CLEANED_DIR}")
