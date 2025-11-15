import nltk
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer
import re

nltk.download('stopwords')
nltk.download('rslp')

def ensure_nltk_resources():
    """Garante que os recursos NLTK necessários estejam disponíveis.
    Não faz downloads desnecessários em cada importação.
    """
    try:
        stopwords.words("portuguese")
    except LookupError:
        nltk.download("stopwords")
    # RSLPStemmer não precisa de download separado, mas deixamos guardado

def preprocess_text(text: str) -> str:
    """
    Limpeza simples do texto em português:
    - remove pontuação
    - lowercase
    - remove stopwords
    - aplica stemming RSLP

    Retorna uma string com tokens "limpos" adequada para classificação baseada em regras
    ou para enviar ao modelo de AI.
    """
    if not text:
        return ""

    # normalizar: manter letras e números (inclui acentos)
    text = re.sub(r"[^\w\sà-úÀ-Ú]", " ", text, flags=re.UNICODE).lower()
    words = text.split()
    try:
        stop_words = set(stopwords.words("portuguese"))
    except Exception:
        stop_words = set()

    stemmer = RSLPStemmer()
    filtered = []
    for w in words:
        if w and w not in stop_words:
            try:
                filtered.append(stemmer.stem(w))
            except Exception:
                filtered.append(w)
    return " ".join(filtered)