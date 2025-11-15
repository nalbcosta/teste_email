# TESTE_EMAIL

Aplicação simples para classificar emails (Produtivo / Improdutivo) e sugerir respostas automáticas.

## Run locally

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

### Multi-provider (Groq / OpenAI / Regra)

Adicione ao `.env` conforme desejar:

```
LLM_PROVIDER=groq       # valores: groq | openai | rule
GROQ_API_KEY=your_groq_key
GROQ_MODEL=mixtral-8x7b-32768
# OpenAI (opcional fallback)
OPENAI_API_KEY=sk_...
OPENAI_MODEL=gpt-3.5-turbo
```

Prioridade de uso:
- Se `LLM_PROVIDER=groq` e houver `GROQ_API_KEY`, usa Groq; caso falhe tenta OpenAI; senão regra.
- Se `LLM_PROVIDER=openai` procede inverso (OpenAI -> Groq -> regra).
- Se `LLM_PROVIDER=rule` sempre regra (sem custo de API).

Observações:
- Sem nenhuma chave definida cai no classificador de regras local.
- Suporta upload de `.txt` e `.pdf` e entrada direta de texto.
