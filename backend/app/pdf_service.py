import uuid
from io import BytesIO
from pypdf import PdfReader

document_store = {}

async def process_pdf(file_bytes: bytes, filename: str) -> dict:
    reader = PdfReader(BytesIO(file_bytes))
    
    text = ""
    num_pages = len(reader.pages)
    
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    
    # Generamos un ID único (document_id)
    doc_id = str(uuid.uuid4())
    
    # Guardamos el texto asociado al ID en nuestro "almacenamiento"
    document_store[doc_id] = {
        "filename": filename,
        "content": text
    }
    
    return {
        "document_id": doc_id,
        "filename": filename,
        "status": "processed",
        "pages": num_pages
    }