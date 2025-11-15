import json
from typing import Dict, Any
from app.core import config

def _rule_based_classify_and_respond(text: str) -> Dict[str, Any]:
    """Classificador simples por palavras-chave quando não há chave de API."""
    prod_keywords = [
        "erro", "problema", "ajuda", "suporte", "favor", "por favor",
        "solicito", "solicitação", "dúvida", "pendente", "status", "atualização"
    ]
    impr_keywords = [
        "obrigado", "obrigada", "feliz", "parabéns", "bom dia", "boa tarde",
        "agradecimento"
    ]
    lowered = text.lower()
    score_prod = sum(1 for k in prod_keywords if k in lowered)
    score_impr = sum(1 for k in impr_keywords if k in lowered)
    if score_prod >= score_impr:
        classification = "Produtivo"
        suggested = (
            "Obrigado pelo contato. Vamos analisar sua solicitação e retornaremos com uma atualização em breve. "
            "Caso precise priorizar, por favor informe."
        )
    else:
        classification = "Improdutivo"
        suggested = (
            "Agradecemos sua mensagem. No momento não é necessária ação adicional. Tenha um ótimo dia."
        )
    return {"classification": classification, "suggested_response": suggested}


def _build_prompt(text: str) -> str:
    return f"""
Você é um assistente corporativo de uma empresa financeira. Analise o email abaixo.

Tarefas:
1. Classifique como "Produtivo" (requer ação, suporte, dúvida) ou "Improdutivo" (spam, felicitações, agradecimento).
2. Gere uma resposta polida e profissional adequada à classificação.

Email: "{text}"

Responda ESTRITAMENTE neste formato JSON:
{{
    "classification": "Produtivo" or "Improdutivo",
    "suggested_response": "Texto da resposta sugerida..."
}}
""".strip()


from typing import Optional


def _call_groq(prompt: str) -> Optional[str]:
    if not config.GROQ_API_KEY:
        return None
    try:
        from groq import Groq
        client = Groq(api_key=config.GROQ_API_KEY)
        completion = client.chat.completions.create(
            model=config.GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=400,
        )
        content = completion.choices[0].message.content
        return content
    except Exception:
        return None


def _call_openai(prompt: str) -> Optional[str]:
    if not config.OPENAI_API_KEY:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=config.OPENAI_API_KEY)
        completion = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=400,
            response_format={"type": "json_object"},
        )
        content = completion.choices[0].message.content
        return content
    except Exception:
        return None


def _call_llm(prompt: str) -> Optional[str]:
    provider = config.LLM_PROVIDER
    if provider == "groq":
        content = _call_groq(prompt)
        if content:
            return content
        # fallback openai
        return _call_openai(prompt)
    elif provider == "openai":
        content = _call_openai(prompt)
        if content:
            return content
        # fallback groq
        return _call_groq(prompt)
    else:
        # provider == 'rule' força fallback
        return None


def _parse_json(content: str, original_text: str) -> Dict[str, Any]:
    try:
        parsed = json.loads(content.strip())
    except Exception:
        # tentativa de extrair bloco JSON delimitado
        import re
        match = re.search(r"\{[\s\S]*\}", content)
        if not match:
            return _rule_based_classify_and_respond(original_text)
        try:
            parsed = json.loads(match.group(0))
        except Exception:
            return _rule_based_classify_and_respond(original_text)
    cls = parsed.get("classification", "").lower()
    if cls.startswith("prod"):
        parsed["classification"] = "Produtivo"
    elif cls.startswith("improd"):
        parsed["classification"] = "Improdutivo"
    else:
        rb = _rule_based_classify_and_respond(original_text)
        parsed["classification"] = rb["classification"]
        parsed.setdefault("suggested_response", rb["suggested_response"])
    if not parsed.get("suggested_response"):
        parsed["suggested_response"] = _rule_based_classify_and_respond(original_text)["suggested_response"]
    return parsed


def classify_and_respond(text: str) -> Dict[str, Any]:
    """Classifica e gera resposta usando Groq ou OpenAI conforme provider, com fallback local."""
    prompt = _build_prompt(text)
    content = _call_llm(prompt)
    if content is None:
        return _rule_based_classify_and_respond(text)
    try:
        return _parse_json(content, text)
    except Exception as e:
        return {
            "classification": "Produtivo",
            "suggested_response": f"Erro ao processar resposta AI ({e}). Usando resposta padrão.",
        }
