import spacy
import re
import subprocess
import sys

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")


def clean_text(text):
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = text.encode('ascii', errors='ignore').decode()
    return text.strip()

def extract_keywords(text, top_n=30):
    doc = nlp(text.lower())
    tokens = [
        token.lemma_ for token in doc
        if token.pos_ in {"NOUN", "PROPN"}
        and not token.is_stop
        and token.is_alpha
    ]
    freq = {}
    for token in tokens:
        freq[token] = freq.get(token, 0) + 1
    return sorted(freq, key=freq.get, reverse=True)[:top_n]

def parse_resume_keywords(raw_text):
    clean = clean_text(raw_text)
    return {
        "keywords": extract_keywords(clean)
    }
