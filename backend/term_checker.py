import os

# Path to cleaned docs
input_dir = "C:\Projects\HybridSearchEngine\data/cleaned_docs"

def check_term(term):
    term = term.lower()
    found_docs = []
    for filename in os.listdir(input_dir):
        if filename.endswith(".txt"):
            path = os.path.join(input_dir, filename)
            with open(path, "r", encoding="utf-8") as f:
                text = f.read().lower()
                if term in text.split():
                    found_docs.append(filename)
    return found_docs

def check_phrase(phrase):
    phrase = phrase.lower()
    found_docs = []
    for filename in os.listdir(input_dir):
        if filename.endswith(".txt"):
            path = os.path.join(input_dir, filename)
            with open(path, "r", encoding="utf-8") as f:
                text = f.read().lower()
                if phrase in text:
                    found_docs.append(filename)
    return found_docs

if __name__ == "__main__":
    while True:
        choice = input("\nSearch for (1) single term or (2) phrase (3 to exit): ").strip()
        if choice == "1":
            term = input("Enter single term: ").strip()
            results = check_term(term)
            print(f"\n→ Found '{term}' in {len(results)} docs: {results[:10]}")
        elif choice == "2":
            phrase = input("Enter phrase: ").strip()
            results = check_phrase(phrase)
            print(f"\n→ Found '{phrase}' in {len(results)} docs: {results[:10]}")
        elif choice == "3":
            print("Exiting.")
            break
        else:
            print("Invalid choice.")
