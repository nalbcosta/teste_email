import nltk
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer
import re

nltk.download('stopwords')
nltk.download('rslp')

# Inicializar função de preprocessamento de texto
def preprocess_text(text):
    # Fazer a limpez inicial do texto
    text = re.sub(r'[^\w\s]', '', text).lower()

    # Stopwords em português
    stop_words = set(stopwords.words('portuguese'))
    words = text.split()

    # Fazer a filtragem e Stemming
    filtered_text = [word for word in words if word not in stop_words]

    return " ".join(filtered_text)