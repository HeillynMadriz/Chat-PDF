import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from app.schemas import ChatRequest
from app.pdf_service import extract_text_from_pdf
from app.chat_service import stream_openrouter

app = FastAPI()

# Configuración de CORS para permitir peticiones del frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Diccionario en memoria para almacenar la base de datos vectorial de cada documento
document_store = {}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    # Volvemos a la validación por extensión que es 100% segura
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="El archivo debe ser un PDF válido.")
    
    file_bytes = await file.read()
    
    # Extraemos el texto y creamos los vectores
    vectorstore = await extract_text_from_pdf(file_bytes)
    
    document_id = str(uuid.uuid4())
    
    # Guardamos la base de datos vectorial de este documento
    document_store[document_id] = {
        "vectorstore": vectorstore,
        "filename": file.filename
    }
    
    return {"document_id": document_id, "message": "PDF procesado exitosamente"}

@app.post("/chat")
async def chat_with_pdf(request: ChatRequest):
    if request.document_id not in document_store:
        raise HTTPException(status_code=404, detail="Documento no encontrado. Por favor, súbelo de nuevo.")
    
    # 1. Recuperamos la base de datos vectorial del documento
    vectorstore = document_store[request.document_id]["vectorstore"]
    
    # 2. MAGIA: Buscamos matemáticamente los 4 fragmentos que más se parecen a la pregunta
    relevant_docs = vectorstore.similarity_search(request.question, k=4)
    
    # 3. Unimos solo esos 4 pedacitos para dárselos a la IA
    doc_context = "\n\n---\n\n".join([doc.page_content for doc in relevant_docs])
    
    # 4. Enviamos la pregunta junto con el contexto hiper-reducido
    return StreamingResponse(
        stream_openrouter(doc_context, request.question),
        media_type="text/event-stream"
    )