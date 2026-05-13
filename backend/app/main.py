# app/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Importamos nuestros servicios y esquemas
from app.pdf_service import process_pdf, document_store
from app.schemas import ChatRequest
from app.chat_service import ask_openrouter

app = FastAPI(title="Web Chat PDF API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="El archivo debe ser un documento PDF")
    
    contents = await file.read()
    result = await process_pdf(contents, file.filename)
    return result

# --- NUEVO ENDPOINT DE CHAT ---
@app.post("/chat")
async def chat_with_pdf(request: ChatRequest):
    # 1. Verificar si el ID del documento existe en nuestra memoria
    if request.document_id not in document_store:
        raise HTTPException(status_code=404, detail="Documento no encontrado o expirado. Por favor, súbelo de nuevo.")
    
    # 2. Extraer el texto del PDF que guardamos en la Fase 2
    doc_context = document_store[request.document_id]["content"]
    
    # 3. Llamar a OpenRouter enviándole el texto y la pregunta
    try:
        answer = await ask_openrouter(doc_context, request.question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al comunicarse con la IA: {str(e)}")