import io
from pypdf import PdfReader
# ¡Aquí está la corrección! Usamos langchain_text_splitters
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Inicializamos el modelo local que convertirá texto a números
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

async def extract_text_from_pdf(file_bytes: bytes):

    # Extraer texto crudo del PDF
    reader = PdfReader(io.BytesIO(file_bytes))

    raw_text = ""

    for page in reader.pages:
        text = page.extract_text()

        if text:
            raw_text += text + "\n"

    # Validar PDF vacío o sin texto
    if not raw_text.strip():
        raise ValueError(
            "El PDF no contiene texto legible."
        )

            
    # Picar el texto en Chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200, 
        length_function=len
    )
    chunks = text_splitter.split_text(raw_text)

    # Convertir a Vectores y guardar en FAISS
    vectorstore = FAISS.from_texts(chunks, embeddings)

    return vectorstore