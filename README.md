# 📧 Classificador Inteligente de Emails

> Solução automatizada para classificação de emails corporativos utilizando Inteligência Artificial

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.121.2-009688.svg)](https://fastapi.tiangolo.com/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-38bdf8.svg)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🎯 Sobre o Projeto

Sistema web desenvolvido para automatizar a leitura e classificação de emails em ambientes corporativos, especialmente no setor financeiro. A aplicação utiliza **Inteligência Artificial** para categorizar emails e sugerir respostas automáticas, otimizando o tempo da equipe.

### Funcionalidades Principais

- **🤖 Classificação Inteligente**: Categoriza emails em "Produtivo" (requer ação) ou "Improdutivo" (sem necessidade de resposta)
- **💬 Respostas Automáticas**: Sugere respostas profissionais adequadas ao contexto de cada email
- **📎 Upload de Arquivos**: Suporta arquivos `.txt` e `.pdf` ou entrada direta de texto
- **📊 Processamento em Lote**: Analisa múltiplos emails simultaneamente com interface accordion
- **🎨 Interface Moderna**: Design responsivo com Tailwind CSS e tema dark/light
- **🔄 Multi-Provider AI**: Suporte para Groq (gratuito), OpenAI e classificador local baseado em regras

## 🏗️ Arquitetura Técnica

### Stack Tecnológico

**Backend:**
- **FastAPI** 0.121.2 - Framework web moderno e performático
- **Python** 3.11+ - Linguagem principal
- **NLTK** - Processamento de linguagem natural (stopwords, RSLP stemming)
- **PyPDF** - Extração de texto de arquivos PDF
- **Groq SDK** - Integração com modelos Llama 3.1 gratuitos
- **OpenAI SDK** - Fallback para GPT-3.5-turbo

**Frontend:**
- **Tailwind CSS** 3.4 - Framework CSS utilitário
- **JavaScript Vanilla** - Lógica de interface sem dependências
- **Jinja2** - Template engine para HTML

**DevOps:**
- **Docker** - Containerização multi-stage
- **Uvicorn** - Servidor ASGI de alta performance
- **Pytest** - Testes automatizados

### Fluxo de Processamento

```
1. Upload/Input → 2. Pré-processamento (NLTK) → 3. Classificação (AI/Rules)
                                                          ↓
5. Exibição UI ← 4. Geração de Resposta ← 3. Parse JSON/Array
```

## 🚀 Deploy no Render

### Pré-requisitos

1. Conta no [Render](https://render.com) (gratuita)
2. Conta no [Groq](https://console.groq.com) para API key gratuita (opcional)
3. Repositório Git com o código

### Passo a Passo

#### 1. Configurar Variáveis de Ambiente

No dashboard do Render, adicione as seguintes variáveis:

```bash
# Obrigatório - Provider de AI (groq recomendado - gratuito)
LLM_PROVIDER=groq

# Groq (gratuito - recomendado)
GROQ_API_KEY=sua_chave_groq_aqui
GROQ_MODEL=llama-3.1-8b-instant

# OpenAI (opcional - pago)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-3.5-turbo
```

**⚠️ Importante**: Se não configurar nenhuma API key, o sistema usa classificador local baseado em regras (sem custo, mas menos preciso).

#### 2. Configurar Build

**Build Command:**
```bash
pip install -r requirements.txt && npm install && npm run tailwind:build
```

**Start Command:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

#### 3. Deploy

- Conecte seu repositório GitHub
- Selecione o branch `main`
- Clique em "Deploy"

O Render automaticamente:
- Instala dependências Python
- Compila Tailwind CSS
- Baixa recursos NLTK
- Inicia o servidor na porta dinâmica

## 💻 Execução Local

### Instalação

```bash
# Clone o repositório
git clone https://github.com/nalbcosta/teste_email.git
cd teste_email

# Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instale dependências
pip install -r requirements.txt
npm install
```

### Configuração

Crie arquivo `.env` na raiz a partir do `.env.example`:

```env
LLM_PROVIDER=groq
GROQ_API_KEY=sua_chave_groq
GROQ_MODEL=llama-3.1-8b-instant
```

### Build e Execução

```bash
# Compile Tailwind CSS
npm run tailwind:build

# Inicie servidor de desenvolvimento
uvicorn app.main:app --reload
```

Acesse: http://127.0.0.1:8000

## 🐳 Docker

```bash
# Build
docker build -t email-classifier .

# Run
docker run -p 8000:8000 \
  -e LLM_PROVIDER=groq \
  -e GROQ_API_KEY=sua_chave \
  email-classifier
```

## 🧪 Testes

O arquivo `test_emails.txt` contém 6 emails de exemplo (3 produtivos + 3 improdutivos) para validação:

```bash
# Executar testes
pytest tests/ -v

# Com coverage
pytest tests/ --cov=app --cov-report=html
```

## 📊 Exemplos de Uso

### 1. Email Produtivo
**Input:**
```
Preciso urgentemente do status da minha solicitação de empréstimo. 
Documentos pendentes?
```

**Output:**
- **Classificação**: Produtivo
- **Resposta Sugerida**: "Olá! Vamos verificar o status da sua solicitação. 
  Pode fornecer mais informações sobre os documentos pendentes? 
  Estamos à disposição."

### 2. Email Improdutivo
**Input:**
```
Feliz Natal para toda equipe! Desejo um 2025 próspero.
```

**Output:**
- **Classificação**: Improdutivo
- **Resposta Sugerida**: "Obrigado pela mensagem! Desejamos também um excelente 
  ano novo. Atenciosamente, Equipe."

## 🎨 Features Visuais

- ✅ **Dark Mode**: Toggle persistente com localStorage
- ✅ **Accordion UI**: Exibição elegante de múltiplos emails
- ✅ **Loading Overlay**: Feedback visual durante processamento
- ✅ **Histórico de Sessão**: Últimas 10 classificações com badges coloridas
- ✅ **Responsive Design**: Funciona perfeitamente em mobile/tablet/desktop
- ✅ **Animations**: Transições suaves e micro-interações

## 🔧 Estrutura do Projeto

```
teste_email/
├── app/
│   ├── core/
│   │   └── config.py          # Configurações e env vars
│   ├── services/
│   │   ├── aI_service.py      # Lógica de classificação AI
│   │   └── nlp_service.py     # Pré-processamento NLTK
│   ├── templates/
│   │   └── index.html         # Template principal
│   ├── utils/
│   │   └── file_parser.py     # Parser de TXT/PDF
│   └── main.py                # FastAPI app
├── static/
│   ├── css/
│   │   └── app.css            # Tailwind compilado
│   └── js/
│       └── app.js             # Lógica frontend
├── tests/
│   └── test_process.py        # Testes automatizados
├── Dockerfile                 # Multi-stage build
├── requirements.txt           # Dependências Python
├── package.json               # Dependências Node (Tailwind)
├── tailwind.config.js         # Configuração Tailwind
└── test_emails.txt            # Emails de exemplo
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👨‍💻 Autor
Nalbert Costa - [GitHub](https://github.com/nalbcosta)
Desenvolvido como parte do desafio técnico AutoU para demonstrar habilidades em:
- Desenvolvimento Full Stack
- Integração de APIs de AI
- Processamento de Linguagem Natural
- Design de Interface Moderna
- DevOps e Deploy em Cloud

---

**🔗 Links Úteis:**
- [Groq API Documentation](https://console.groq.com/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Render Deploy Guide](https://render.com/docs)
