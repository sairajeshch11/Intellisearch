import json

count = 0
with open("data/docs.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            json.loads(line)
            count += 1

print(f"Total documents in dataset: {count}")

