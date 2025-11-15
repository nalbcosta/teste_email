import json
import re
from typing import Dict, Any, Optional
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
    lowered = (text or "").lower()
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


def _call_groq(prompt: str) -> Optional[str]:
    """Tenta chamar o Groq se a chave estiver configurada. Retorna string ou None."""
    if not config.GROQ_API_KEY:
        return None
    try:
        from groq import Groq
        client = Groq(api_key=config.GROQ_API_KEY)
        completion = client.chat.completions.create(
            model=config.GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=2048,
        )
        try:
            content = completion.choices[0].message.content
        except Exception:
            content = getattr(completion.choices[0], "text", None) or None
        return content
    except Exception as e:
        print(f"Erro ao chamar Groq: {e}")
        return None


def _call_openai(prompt: str) -> Optional[str]:
    """Tenta chamar OpenAI se a chave estiver configurada. Retorna string ou None."""
    if not config.OPENAI_API_KEY:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=config.OPENAI_API_KEY)
        completion = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=2048,
            response_format={"type": "json_object"},
        )
        try:
            content = completion.choices[0].message.content
        except Exception:
            content = getattr(completion.choices[0], "text", None) or None
        return content
    except Exception as e:
        print(f"Erro ao chamar OpenAI: {e}")
        return None


def _call_llm(prompt: str) -> Optional[str]:
    provider = getattr(config, "LLM_PROVIDER", "groq")
    provider = (provider or "").lower()
    if provider == "groq":
        content = _call_groq(prompt)
        if content:
            return content
        return _call_openai(prompt)
    elif provider == "openai":
        content = _call_openai(prompt)
        if content:
            return content
        return _call_groq(prompt)
    else:
        return None


def _parse_json(content: str, original_text: str) -> Dict[str, Any]:
    """Tenta extrair e normalizar JSON vindo do LLM.

    Suporta:
    - JSON objeto (dict) com keys 'classification' e 'suggested_response'
    - JSON array (list) onde cada item é um objeto com as mesmas keys
    - Texto com bloco ```json ...``` contendo um array/objeto
    """
    if not content:
        rb = _rule_based_classify_and_respond(original_text)
        rb["is_multiple"] = False
        return rb

    # tenta carregar diretamente
    try:
        parsed = json.loads(content.strip())
    except Exception:
        # tenta extrair primeiro bloco JSON (objeto ou array)
        match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", content)
        if not match:
            rb = _rule_based_classify_and_respond(original_text)
            rb["is_multiple"] = False
            return rb
        try:
            parsed = json.loads(match.group(0))
        except Exception:
            rb = _rule_based_classify_and_respond(original_text)
            rb["is_multiple"] = False
            return rb

    # Se for lista, normalize e retorne estrutura com items
    if isinstance(parsed, list):
        items = []
        for idx, item in enumerate(parsed, start=1):
            if not isinstance(item, dict):
                continue
            cls = (item.get("classification") or "").lower()
            resp = item.get("suggested_response") or item.get("response") or ""
            normalized_cls = "Produtivo" if cls.startswith("prod") else "Improdutivo"
            items.append({
                "id": idx,
                "classification": normalized_cls,
                "suggested_response": resp or "Sem resposta sugerida."
            })
        if not items:
            rb = _rule_based_classify_and_respond(original_text)
            items = [{"id": 1, "classification": rb["classification"], "suggested_response": rb["suggested_response"]}]
        # overall: se ao menos um for produtivo, marca como produtivo
        overall = "Produtivo" if any(i["classification"] == "Produtivo" for i in items) else "Improdutivo"
        result = {"classification": overall, "items": items, "is_multiple": True}
        return result

    # se for dict
    if not isinstance(parsed, dict):
        rb = _rule_based_classify_and_respond(original_text)
        rb["is_multiple"] = False
        return rb

    cls = (parsed.get("classification", "") or "").lower()
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
    
    parsed["is_multiple"] = False
    return parsed


def classify_and_respond(text: str) -> Dict[str, Any]:
    """Flow principal: constrói prompt, chama LLM configurado e parseia/retorna resultado."""
    prompt = _build_prompt(text)
    content = _call_llm(prompt)
    if content is None:
        return _rule_based_classify_and_respond(text)
    try:
        result = _parse_json(content, text)
        return result
    except Exception as e:
        print(f"Erro ao processar resposta da AI: {e}")
        fallback = _rule_based_classify_and_respond(text)
        fallback["is_multiple"] = False
        return fallback
