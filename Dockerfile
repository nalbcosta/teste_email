# Multi-stage build para otimização
FROM node:18-slim AS tailwind-builder

WORKDIR /app
COPY package*.json tailwind.config.js ./
COPY tailwind ./tailwind
RUN npm ci && npm run tailwind:build

# Imagem final otimizada
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Baixar recursos NLTK necessários
RUN python -c "import nltk; nltk.download('stopwords'); nltk.download('rslp')"

# Copiar código da aplicação
COPY app ./app
COPY static ./static
COPY test_emails.txt ./

# Copiar CSS compilado do Tailwind
COPY --from=tailwind-builder /app/static/css/app.css ./static/css/app.css

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Expor porta
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Comando de inicialização com variável PORT dinâmica
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
