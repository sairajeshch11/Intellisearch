import os
import re
import string

# ✅ Optional: You can use nltk stopwords if installed, else use a simple built-in list
try:
    from nltk.corpus import stopwords
    stop_words = set(stopwords.words('english'))
except:
    # simple built-in fallback stopword list
    stop_words = {
        'a','an','and','the','of','for','to','in','on','is','are','this','that','with','we','by','it','as','be','our','from','or','at'
    }

# Input/output folders
input_dir = "C:\Projects\HybridSearchEngine\data/raw_docs"
output_dir = "C:\Projects\HybridSearchEngine\data/cleaned_docs"
os.makedirs(output_dir, exist_ok=True)

def clean_and_tokenize(text):
    # lowercase
    text = text.lower()
    # remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    # remove numbers
    text = re.sub(r'\d+', '', text)
    # tokenize (split by whitespace)
    tokens = text.split()
    # remove stopwords
    tokens = [t for t in tokens if t not in stop_words]
    return tokens

def preprocess_all():
    files = [f for f in os.listdir(input_dir) if f.endswith(".txt")]
    print(f"Found {len(files)} raw documents.")
    
    for i, file in enumerate(files, 1):
        file_path = os.path.join(input_dir, file)
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        
        tokens = clean_and_tokenize(text)
        cleaned_text = " ".join(tokens)
        
        output_path = os.path.join(output_dir, file)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(cleaned_text)
        
        if i % 100 == 0:
            print(f"Processed {i} / {len(files)} files...")

    print(f"✅ Cleaning complete! Saved cleaned files to {output_dir}")

if __name__ == "__main__":
    preprocess_all()
