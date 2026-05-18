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

# Diccionario en memoria para almacenar la base de datos vectorial
document_store = {}

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):

    # Validar extensión
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="El archivo debe ser un PDF válido."
        )

    file_bytes = await file.read()

    try:
        # Procesar PDF
        vectorstore = await extract_text_from_pdf(file_bytes)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Ocurrió un error al procesar el PDF."
        )

    document_id = str(uuid.uuid4())

    # Guardar vectorstore
    document_store[document_id] = {
        "vectorstore": vectorstore,
        "filename": file.filename
    }

    return {
        "document_id": document_id,
        "message": "PDF procesado exitosamente"
    }


@app.post("/chat")
async def chat_with_pdf(request: ChatRequest):

    # Verificar documento
    if request.document_id not in document_store:
        raise HTTPException(
            status_code=404,
            detail="Documento no encontrado. Por favor, súbelo de nuevo."
        )

    # Recuperar vectorstore
    vectorstore = document_store[request.document_id]["vectorstore"]

    # Buscar fragmentos relacionados
    docs_and_scores = vectorstore.similarity_search_with_score(
        request.question,
        k=4
    )

    # Extraer solo documentos
    relevant_docs = [doc for doc, score in docs_and_scores]

    # Construir contexto
    doc_context = "\n\n---\n\n".join(
        [doc.page_content for doc in relevant_docs]
    )

    # Enviar respuesta streaming
    return StreamingResponse(
        stream_openrouter(doc_context, request.question),
        media_type="text/event-stream"
    )