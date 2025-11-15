import io
from fastapi.testclient import TestClient
from app.main import app
from app.services import nlp_service

# Evitar downloads do NLTK em ambiente de teste
nlp_service.ensure_nltk_resources = lambda: None

client = TestClient(app)

def test_process_produtivo_text():
    resp = client.post('/process', data={'text_input': 'Preciso de ajuda com erro de status pendente no sistema'})
    assert resp.status_code == 200
    data = resp.json()
    assert data['classification'] in ['Produtivo', 'Improdutivo']
    # Deveria cair em produtivo dado as palavras
    assert data['classification'] == 'Produtivo'
    assert 'Obrigado' in data['suggested_response'] or 'Agradecemos' in data['suggested_response']

def test_process_improdutivo_text():
    resp = client.post('/process', data={'text_input': 'Feliz natal e parabéns pelo ótimo trabalho! Obrigado'})
    assert resp.status_code == 200
    data = resp.json()
    assert data['classification'] in ['Produtivo', 'Improdutivo']
    assert data['classification'] == 'Improdutivo'

def test_process_txt_upload():
    content = b'Solicito status da solicitacao pendente de suporte.'
    file = io.BytesIO(content)
    resp = client.post('/process', files={'file': ('email.txt', file, 'text/plain')})
    assert resp.status_code == 200
    data = resp.json()
    assert 'classification' in data
    assert 'suggested_response' in data
