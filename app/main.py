from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
# from app.utils.file_parser import read_file_content
from app.services.nlp_service import preprocess_text
from app.services.aI_service import classify_and_respond

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/process")
async def process_email(
    file: UploadFile = File(None),
    text_input: str = Form(None)
):
    # Obter o conteúdo do email
    content = ""
    if file is not None:
        content = await file.read()
        content = content.decode('utf-8')
    elif text_input is not None:
        content = text_input
    else:
        return {"error": "Nenhum arquivo ou texto fornecido."}
    
    # NLP
    cleaned_content = preprocess_text(content)

    # Classificação e resposta AI
    result = classify_and_respond(cleaned_content)

    return result



