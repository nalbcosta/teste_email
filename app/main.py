from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.utils.file_parser import read_file_content
from app.services.nlp_service import preprocess_text, ensure_nltk_resources
from app.services.aI_service import classify_and_respond
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando aplicação...")
    ensure_nltk_resources()
    yield
    print("Finalizando aplicação...")


app = FastAPI(lifespan=lifespan)

# monta a pasta static (está na raiz do projeto)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/process")
async def process_email(
    file: UploadFile = File(None),
    text_input: str = Form(None)
):
    content = ""
    if file is not None:
        # usar util para ler pdf/txt
        content = read_file_content(file)
    elif text_input:
        content = text_input
    else:
        return {"error": "Nenhum arquivo ou texto fornecido."}

    cleaned_content = preprocess_text(content)
    result = classify_and_respond(cleaned_content)
    return result



