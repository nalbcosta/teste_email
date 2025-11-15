from openai import OpenAI
import json
# from core.config import env.api_key

client = OpenAI(api_key='key')

def classify_and_respond(text: str):
    prompt = f"""
    Você é um assistente corporativo de uma empresa financeira. Analise o email abaixo.
    
    Tarefas:
    1. Classifique como "Produtivo" (requer ação, suporte, dúvida) ou "Improdutivo" (spam, feliz natal, agradecimento solto).
    2. Gere uma resposta polida e profissional adequada à classificação.
    
    Email: "{text}"
    
    Responda ESTRITAMENTE neste formato JSON:
    {{
        "classification": "Produtivo" ou "Improdutivo",
        "suggested_response": "Texto da resposta sugerida..."
    }}
    """

    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[{'role': 'user', 'content': prompt}],
        response_format={'type': 'json_object'}
    )

    content = response.choices[0].message.content
    if content is None:
        raise ValueError("AI response content is None")
    
    return json.loads(content)
