from dotenv import load_dotenv
import os

load_dotenv()

# Carrega chave da OpenAI a partir de variáveis de ambiente (opcional).
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
# Modelo padrão (pode ser substituído via .env)
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

