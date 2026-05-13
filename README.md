# Chat con PDF 📄🤖

## Descripción
Aplicación web full-stack que permite a los usuarios subir un documento PDF y realizar preguntas sobre su contenido mediante una interfaz conversacional. El sistema utiliza SvelteKit para una experiencia de usuario fluida, FastAPI para el procesamiento eficiente del lado del servidor, y consume modelos de lenguaje avanzados a través de la API de OpenRouter.

## Tecnologías
- **Frontend:** SvelteKit, TypeScript, Tailwind CSS.
- **Backend:** FastAPI, Python 3.11+, pypdf.
- **IA:** OpenRouter (SDK oficial de OpenAI).
- **Gestor de paquetes backend:** uv.

## Requisitos Previos
- Node.js (v18 o superior).
- Python 3.11+.
- uv.
- API key válida de OpenRouter.

---

## ⚙️ Instalación y Ejecución (Backend)

**1. Configuración del entorno**
```bash
cd backend
uv sync
```

**2. Variables de entorno**
Crea un archivo `.env` en la carpeta `backend` con las siguientes credenciales:
```env
OPENROUTER_API_KEY=tu_api_key_aqui
OPENROUTER_MODEL=openai/gpt-4o-mini
```

**3. Levantar el servidor**
```bash
uv run uvicorn app.main:app --reload
```
*El backend estará disponible en http://localhost:8000*

---

## 🖥️ Instalación y Ejecución (Frontend)

**1. Configuración del cliente**
En una nueva terminal, instala las dependencias y levanta el cliente:
```bash
cd frontend
npm install
npm run dev
```
*El frontend estará disponible en http://localhost:5173*

---

## 🚀 Uso de la Aplicación
1. Abre tu navegador y dirígete a `http://localhost:5173`.
2. Haz clic en "Elegir archivo PDF" y selecciona un documento local.
3. Haz clic en "Enviar y Procesar Documento".
4. Una vez procesado, utiliza la barra inferior para hacerle preguntas a la IA sobre el contenido del documento.