# app/chat_service.py
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Cargar las variables del archivo .env
load_dotenv()

# Configurar el cliente usando el SDK de OpenAI pero apuntando a OpenRouter
client = AsyncOpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)

async def ask_openrouter(document_context: str, user_question: str) -> str:
    # Esta es la estrategia de prompt exacta que pedía tu rúbrica
    prompt = f"""Eres un asistente que responde preguntas únicamente usando el contenido del PDF proporcionado.

Contenido del PDF:
---
{document_context}
---

Pregunta del usuario:
{user_question}

Instrucciones:
- Responde en español.
- Si la respuesta no está en el PDF, indica que no hay suficiente información.
- No inventes datos.
- Sé claro y directo."""

    # Hacemos la petición a la IA
    response = await client.chat.completions.create(
        model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content or ""