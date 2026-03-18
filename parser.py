import spacy
import json

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Load skills dictionary
with open("skills_dict.json", "r") as f:
    SKILLS_DICT = json.load(f)

def extract_skills(text):
    text = text.lower()
    skills_found = []
    for skill, keywords in SKILLS_DICT.items():
        for kw in keywords:
            if kw.lower() in text:
                skills_found.append(skill)
                break
    return list(set(skills_found))

def extract_text_from_file(file_path):
    text = ""
    if file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    elif file_path.endswith(".pdf"):
        import PyPDF2
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
    return text