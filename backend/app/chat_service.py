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

    prompt = f"""
Eres un asistente especializado en responder preguntas sobre documentos PDF.

Usa el contexto proporcionado como fuente principal de información.

Si el contexto no contiene suficiente detalle para responder completamente,
puedes complementar con conocimiento general relacionado directamente con el tema del documento únicamente si ayuda a explicar mejor información presente en el PDF.

No inventes información.

Si la pregunta no está relacionada con el documento, indícalo claramente.

---
{document_context}
---

Pregunta del usuario:
{user_question}

Instrucciones:
- Responde en español.
- Usa el PDF como fuente principal.
- Solo responde preguntas claramente relacionadas con el tema principal del documento.
- Puedes complementar con conocimiento general únicamente si ayuda a explicar mejor información presente en el PDF.
- No respondas preguntas ambiguas, demasiado generales o que no estén directamente relacionadas con el contenido del documento.
- No asumas que nombres ambiguos o incompletos se refieren a personas mencionadas en el documento.
- Si una pregunta es ambigua o no tiene relación clara con el PDF, pide aclaración o indica amablemente que no parece relacionada con el documento.
- No inventes información.
- Sé claro, útil y amable.
"""

    try:

        response = await client.chat.completions.create(
            model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
        )

        return response.choices[0].message.content or ""

    except Exception:
        return "Ocurrió un error al generar la respuesta."

# ---------------- STREAMING ---------------- #

async def stream_openrouter(
    document_context: str,
    user_question: str
):

    prompt = f"""
Eres un asistente especializado en responder preguntas sobre documentos PDF.

Usa el contexto proporcionado como fuente principal de información.

Si el contexto no contiene suficiente detalle para responder completamente,
puedes complementar con conocimiento general relacionado directamente con el tema del documento únicamente si ayuda a explicar mejor información presente en el PDF.

No inventes información.

Si la pregunta no está relacionada con el documento, indícalo claramente.

---
{document_context}
---

Pregunta del usuario:
{user_question}

Instrucciones:
- Responde en español.
- Usa el PDF como fuente principal.
- Solo responde preguntas claramente relacionadas con el tema principal del documento.
- Puedes complementar con conocimiento general únicamente si ayuda a explicar mejor información presente en el PDF.
- No respondas preguntas ambiguas, demasiado generales o que no estén directamente relacionadas con el contenido del documento.
- No asumas que nombres ambiguos o incompletos se refieren a personas mencionadas en el documento.
- Si una pregunta es ambigua o no tiene relación clara con el PDF, pide aclaración o indica amablemente que no parece relacionada con el documento.
- No inventes información.
- Sé claro, útil y amable.
"""

    try:

        response = await client.chat.completions.create(
            model=os.getenv(
                "OPENROUTER_MODEL",
                "openai/gpt-4o-mini"
            ),
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            stream=True,
        )

        async for chunk in response:

            content = chunk.choices[0].delta.content

            if content:
                yield content

    except Exception:
        yield "Ocurrió un error al generar la respuesta."