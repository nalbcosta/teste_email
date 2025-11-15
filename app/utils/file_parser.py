from fastapi import UploadFile
import io


def read_file_content(upload_file: UploadFile) -> str:
	"""
	Lê o conteúdo de um UploadFile recebido pelo FastAPI.
	Suporta arquivos .txt (ou texto puro) e .pdf.
	Retorna o texto extraído como string.
	"""
	if upload_file is None:
		return ""

	filename = upload_file.filename or ""
	# ler bytes do UploadFile (UploadFile.file é um SpooledTemporaryFile-like)
	content_bytes = upload_file.file.read()
	try:
		if filename.lower().endswith(".pdf"):
			try:
				from pypdf import PdfReader
			except Exception:
				# fallback: não conseguir importar pypdf
				return ""

			reader = PdfReader(io.BytesIO(content_bytes))
			texts = []
			for page in reader.pages:
				texts.append(page.extract_text() or "")
			return "\n".join(texts)
		else:
			# assume texto
			return content_bytes.decode("utf-8", errors="ignore")
	finally:
		try:
			upload_file.file.close()
		except Exception:
			pass

