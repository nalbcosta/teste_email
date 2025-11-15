# TESTE_EMAIL

Aplicação simples para classificar emails (Produtivo / Improdutivo) e sugerir respostas automáticas.

Run locally

1. Copie `.env.example` (ou crie `.env`) e, opcionalmente, adicione sua chave da OpenAI:

```
OPENAI_API_KEY=sk_...
```

2. Instale dependências e rode localmente:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

3. Abra http://127.0.0.1:8000

Observações:
- Se `OPENAI_API_KEY` não estiver definida, o sistema usará um classificador baseado em regras local.
- Suporta upload de `.txt` e `.pdf` e entrada direta de texto.
