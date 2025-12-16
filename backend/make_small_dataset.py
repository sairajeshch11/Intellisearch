import json, re
from pathlib import Path

KEY_TERMS = [
    "machine learning","deep learning","neural network","transformer","llm","large language model",
    "reinforcement learning","classification","clustering","embedding",
    "information retrieval","search engine","bm25","ranking","retrieval","query","index",
    "natural language processing","nlp","question answering","summarization",
    "distributed system","operating system","concurrency","parallel","gpu","cuda",
    "database","sql","data mining","big data",
    "cybersecurity","encryption","privacy","network","protocol",
    "software engineering","testing","debugging","microservices","devops",
]

def score_doc(title: str, abstract: str) -> float:
    t = (title or "").lower()
    a = (abstract or "").lower()
    s = 0.0
    for term in KEY_TERMS:
        if term in t: s += 5.0
        if term in a: s += 2.0
    return s

import json, re
from pathlib import Path

def main():
    in_path = Path(r"C:\Projects\HybridSearchEngine\data\docs.jsonl")
    out_path = Path(r"C:\Projects\HybridSearchEngine\data\docs_2000.jsonl")

    scored = []
    with in_path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            obj = json.loads(line)
            title = obj.get("title", "")
            abstract = obj.get("abstract", obj.get("text", ""))
            scored.append((1, obj))  # scoring already handled earlier

    top = scored[:2000]
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", encoding="utf-8") as w:
        for _, obj in top:
            w.write(json.dumps(obj) + "\n")

    print(f"Wrote {len(top)} docs to {out_path}")

if __name__ == "__main__":
    main()
