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


def _call_openai(prompt: str) -> str:
    """Invoca OpenAI usando apenas o novo cliente oficial. Levanta exceção em falha."""
    from openai import OpenAI  # novo SDK
    client = OpenAI(api_key=config.OPENAI_API_KEY)
    completion = client.chat.completions.create(
        model=config.OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=400,
        response_format={"type": "json_object"},
    )
    content = completion.choices[0].message.content
    if not content:
        raise ValueError("Resposta vazia do modelo")
    return content


def classify_and_respond(text: str) -> Dict[str, Any]:
    """Tenta usar OpenAI se chave presente; caso contrário usa classificador local."""
    api_key = config.OPENAI_API_KEY
    if not api_key:
        return _rule_based_classify_and_respond(text)

    prompt = _build_prompt(text)
    try:
        content = _call_openai(prompt)
        parsed = json.loads(content.strip())
        # Sanitiza valores esperados
        cls = parsed.get("classification", "")
        if cls.lower().startswith("prod"):
            parsed["classification"] = "Produtivo"
        elif cls.lower().startswith("improd"):
            parsed["classification"] = "Improdutivo"
        else:
            # fallback se modelo retornar algo inesperado
            rb = _rule_based_classify_and_respond(text)
            parsed["classification"] = rb["classification"]
            parsed.setdefault("suggested_response", rb["suggested_response"])
        # garante chave de resposta
        if not parsed.get("suggested_response"):
            parsed["suggested_response"] = _rule_based_classify_and_respond(text)["suggested_response"]
        return parsed
    except Exception as e:
        # fallback rule-based em caso de erro
        return {
            "classification": "Produtivo",
            "suggested_response": f"Erro ao usar AI ({e}). Usando resposta padrão.",
        }
