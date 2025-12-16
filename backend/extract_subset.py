import json
import os

input_path = "C:/Projects/HybridSearchEngine/data/arxiv-metadata-oai-snapshot.json"
output_dir = "C:/Projects/HybridSearchEngine/data/raw_docs"
os.makedirs(output_dir, exist_ok=True)

count = 0
limit = 20000  # extract 20K papers

with open(input_path, "r", encoding="utf-8") as infile:
    for line in infile:
        if count >= limit:
            break
        try:
            paper = json.loads(line)
            title = paper.get("title", "").strip()
            abstract = paper.get("abstract", "").strip()
            if title and abstract:
                text = f"{title}\n\n{abstract}"
                with open(os.path.join(output_dir, f"paper_{count+1}.txt"), "w", encoding="utf-8") as f:
                    f.write(text)
                count += 1
        except Exception as e:
            continue

print(f"✅ Extracted {count} papers into {output_dir}")


import os
files = os.listdir("C:\Projects\HybridSearchEngine\data/raw_docs")
print("Number of text files:", len(files))
print("Example file content:\n")
with open(f"C:\Projects\HybridSearchEngine\data/raw_docs/{files[0]}", 'r', encoding='utf-8') as f:
    print(f.read()[:411])
