from dotenv import load_dotenv
import os

load_dotenv()

# Provedor primário de LLM: 'groq' | 'openai' | 'rule'
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()

# Groq (modelos open-source acelerados). Ex: mixtral-8x7b-32768, llama-3.1-70b-versatile
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")

# OpenAI (fallback opcional)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")


