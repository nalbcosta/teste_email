# Multi-stage build para otimização
FROM node:18-slim AS tailwind-builder

WORKDIR /app
COPY package*.json tailwind.config.js ./
COPY tailwind ./tailwind
COPY app/templates ./app/templates
COPY static ./static
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
COPY start.sh ./

# Copiar CSS compilado do Tailwind
COPY --from=tailwind-builder /app/static/css/app.css ./static/css/app.css

# Dar permissão de execução ao script
RUN chmod +x start.sh

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1

# Expor porta
EXPOSE 8000

# Comando de inicialização com variável PORT dinâmica
CMD ["./start.sh"]
