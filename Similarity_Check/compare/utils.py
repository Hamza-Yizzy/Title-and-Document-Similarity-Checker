# compare/utils.py
import docx
import fitz  # PyMuPDF
from difflib import SequenceMatcher

def extract_file_content(file):
    try:
        if file.name.endswith('.txt'):
            return file.read().decode('utf-8')
        elif file.name.endswith('.docx'):
            doc = docx.Document(file)
            return "\n".join([p.text for p in doc.paragraphs])
        elif file.name.endswith('.pdf'):
            text = ''
            with fitz.open(stream=file.read(), filetype='pdf') as doc:
                for page in doc:
                    text += page.get_text()
            return text
        else:
            return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def calculate_similarity(text1, text2):
    return SequenceMatcher(None, text1, text2).ratio()
