<script lang="ts">
    import { onMount } from 'svelte';
    import { Pencil, Copy, Trash2, Send} from 'lucide-svelte';
    import { Check } from 'lucide-svelte'; 

    let isDarkMode = $state(false);
    let fileInput = $state<HTMLInputElement | null>(null);
    let chatContainer = $state<HTMLDivElement | null>(null);
    let uploadStatus = $state('');
    let documentId = $state('');
    let selectedFileName = $state('');

    let question = $state('');
    let messages = $state<
    {
        role: string;
        text: string;
        copied?: boolean;
        editing?: boolean;
    }[]
    >([]);
    let isAsking = $state(false);
    let editingIndex = $state<number | null>(null);
    let editedText = $state('');

    onMount(() => {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark' || (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
            isDarkMode = true;
            document.documentElement.classList.add('dark');
            document.body.style.background = "linear-gradient(135deg, #0f172a, #020617)";
        } else {
            document.body.style.background = "linear-gradient(135deg, #f8fafc, #e2e8f0)";
        }

        const savedDocId = localStorage.getItem('chat_doc_id');
        const savedMessages = localStorage.getItem('chat_messages');
        const savedFileName = localStorage.getItem('chat_file_name');

        if (savedDocId && savedMessages) {
            documentId = savedDocId;
            messages = JSON.parse(savedMessages);
            if (savedFileName) selectedFileName = savedFileName;
        }
    });

    $effect(() => {
        if (documentId) {
            localStorage.setItem('chat_doc_id', documentId);
            localStorage.setItem('chat_messages', JSON.stringify(messages));
            localStorage.setItem('chat_file_name', selectedFileName);
            scrollToBottom();
        }
    });

    function toggleDarkMode() {
        isDarkMode = !isDarkMode;
        if (isDarkMode) {
    document.documentElement.classList.add('dark');
    document.body.style.background =
        'linear-gradient(135deg, #0f172a, #020617)';
    localStorage.setItem('theme', 'dark');
} else {
    document.documentElement.classList.remove('dark');
    document.body.style.background =
        'linear-gradient(135deg, #f8fafc, #e2e8f0)';
    localStorage.setItem('theme', 'light');
}
    }

    function scrollToBottom() {
        if (chatContainer) {
            chatContainer.scrollTo({
                top: chatContainer.scrollHeight,
                behavior: 'smooth'
            });
        }
    }

    function resetChat() {
        localStorage.removeItem('chat_doc_id');
        localStorage.removeItem('chat_messages');
        localStorage.removeItem('chat_file_name');
        documentId = '';
        messages = [];
        selectedFileName = '';
        uploadStatus = '';
        question = '';
        if (fileInput) fileInput.value = '';
    }

    function handleFileChange() {
        const file = fileInput?.files?.[0];
        if (file) {
            selectedFileName = file.name;
            uploadStatus = ''; 
        }
    }

    async function handleUpload() {
        const file = fileInput?.files?.[0];
        if (!file) return;

        uploadStatus = '⏳ Procesando documento en el servidor...';
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('http://localhost:8000/upload-pdf', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const data = await response.json();
                documentId = data.document_id;
                messages = [{ role: 'assistant', text: `¡Hola! He analizado "${selectedFileName}". ¿En qué puedo ayudarte?` }];
            } else {
                uploadStatus = '❌ Error al procesar el PDF.';
            }
        } catch {
            uploadStatus = '❌ Error de conexión.';
        }
    }

async function handleAsk() {

    if (!question.trim() || isAsking) return;

    messages = [
        ...messages,
        {
            role: 'user',
            text: question
        }
    ];

    const currentQuestion = question;

    question = '';

    isAsking = true;

    try {

        const response = await fetch(
            'http://localhost:8000/chat',
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    document_id: documentId,
                    question: currentQuestion
                })
            }
        );

        // Manejo de errores backend
        if (!response.ok) {

            const errorData = await response.json();

            messages = [
                ...messages,
                {
                    role: 'assistant',
                    text:
                        `❌ ${errorData.detail || 'Ocurrió un error.'}`
                }
            ];

            return;
        }

        // Crear mensaje vacío streaming
        messages = [
            ...messages,
            {
                role: 'assistant',
                text: ''
            }
        ];

        const reader = response.body?.getReader();

        const decoder = new TextDecoder();

        if (reader) {

            while (true) {

                const { done, value } =
                    await reader.read();

                if (done) break;

                const textChunk = decoder.decode(
                    value,
                    { stream: true }
                );

                messages[messages.length - 1].text += textChunk;

                messages = [...messages];
            }
        }

    } catch {

        messages = [
            ...messages,
            {
                role: 'assistant',
                text:
                    '❌ No se pudo conectar con el servidor.'
            }
        ];

    } finally {

        isAsking = false;
    }
}

    async function copyMessage(
    text: string,
    index: number
) {

    try {

        await navigator.clipboard.writeText(text);

        messages[index].copied = true;

        messages = [...messages];

        setTimeout(() => {

            messages[index].copied = false;

            messages = [...messages];

        }, 2000);

    } catch {

        alert('No se pudo copiar el mensaje.');
    }
}

function startEdit(index: number) {
    editingIndex = index;
    editedText = messages[index].text;
}

function cancelEdit() {
    editingIndex = null;
    editedText = '';
}

async function saveEdit(index: number) {
    if (!editedText.trim()) return;

    // 1. Actualizas el mensaje del usuario
    messages[index].text = editedText;

    // 2. Eliminas cualquier mensaje posterior (respuesta anterior del bot)
    messages = messages.slice(0, index + 1);

    // 3. Limpias estado de edición
    editingIndex = null;
    editedText = '';

    // 4. Re-enviar la pregunta editada
    const questionToResend = messages[index].text;

    isAsking = true;

    try {
        const response = await fetch('http://localhost:8000/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                document_id: documentId,
                question: questionToResend
            })
        });

        if (!response.ok) return;

        messages = [...messages, { role: 'assistant', text: '' }];

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();

        if (reader) {
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });

                messages[messages.length - 1].text += chunk;
                messages = [...messages];
            }
        }

    } finally {
        isAsking = false;
    }
}

</script>

<main style="max-width: 700px; margin: 3rem auto; font-family: sans-serif; display: flex; flex-direction: column; height: 85vh; padding: 0 1rem; transition: all 0.3s;">
    
    <div style="display: flex; justify-content: flex-end; margin-bottom: 0.5rem;">
        <button onclick={toggleDarkMode} style="background: none; border: none; cursor: pointer; font-size: 1.8rem; outline: none; transition: transform 0.2s;">
            {isDarkMode ? '🌙' : '☀️'}
        </button>
    </div>

    <h1 style="text-align: center; font-size: 2.2rem; font-weight: bold; margin-bottom: 0.5rem; transition: color 0.3s; color: {isDarkMode ? 'white' : '#1e293b'};">
        Chat PDF 
    </h1>
    
    {#if !documentId}
        <div style="padding: 3rem 2rem; 
        border: 1px solid {isDarkMode ? 'rgba(148,163,184,0.2)' : 'rgba(148,163,184,0.3)'};
        border-radius: 16px; 
        background: {isDarkMode
            ? 'rgba(30,41,59,0.6)'
            : 'rgba(255,255,255,0.6)'};
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        text-align: center; 
        margin-top: 2rem; 
        transition: all 0.3s; 
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
            <p style="color: {isDarkMode ? '#94a3b8' : '#64748b'}; margin-bottom: 2rem; font-size: 1.1rem;">Sube un documento para comenzar la conversación.</p>
            
            <label style="cursor: pointer; padding: 0.8rem 1.8rem; background-color: {isDarkMode ? '#334155' : '#f1f5f9'}; color: {isDarkMode ? 'white' : '#334155'}; border-radius: 8px; font-weight: bold; display: inline-block; transition: background 0.2s;">
                Elegir archivo PDF
                <input type="file" accept=".pdf" bind:this={fileInput} onchange={handleFileChange} style="display: none;" />
            </label>

            {#if selectedFileName}
                <div style="margin-top: 2rem;">
                    <p style="margin-bottom: 1rem; color: {isDarkMode ? 'white' : '#0f172a'};">Seleccionado: <strong>{selectedFileName}</strong></p>
                    <button onclick={handleUpload} style="cursor: pointer; padding: 0.8rem 2rem; background-color: #2563eb; color: white; border: none; border-radius: 8px; font-weight: bold; font-size: 1rem; box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);">
                        Empezar Chat
                    </button>
                </div>
            {/if}

            {#if uploadStatus}
                <p style="margin-top: 1.5rem; color: {isDarkMode ? '#cbd5e1' : '#475569'};">{uploadStatus}</p>
            {/if}
        </div>

    {:else}
        <div style="flex: 1; display: flex; flex-direction: column; border: 1px solid {isDarkMode ? '#334155' : '#e2e8f0'}; border-radius: 16px; overflow: hidden; background: transparent;; margin-top: 1rem; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05); transition: all 0.3s;">
            
            <div style="padding: 0.8rem 1.5rem; background-color: {isDarkMode ? '#1e293b' : '#f8fafc'}; border-bottom: 1px solid {isDarkMode ? '#334155' : '#e2e8f0'}; display: flex; justify-content: space-between; align-items: center; transition: all 0.3s;">
                <span style="color: {isDarkMode ? '#cbd5e1' : '#475569'}; font-size: 0.9rem; font-weight: 600;">
                    💬 {selectedFileName}
                </span>
                <button 
                    onclick={resetChat} 
                     style="background:none;border:none;cursor:pointer;">
                    <Trash2 size={18} />
               
                </button>
            </div>

            <div bind:this={chatContainer} style="flex: 1; overflow-y: auto; padding: 1.5rem; display: flex; flex-direction: column; gap: 1rem; background-color: {isDarkMode ? '#0f172a' : '#ffffff'}; transition: all 0.3s;">
                {#each messages as msg, index (index)}
                

    <div
        style="
            display: flex;
            justify-content:
                {msg.role === 'user'
                    ? 'flex-end'
                    : 'flex-start'};
        "
    >

        <div
            style="
                max-width: 85%;
                padding: 0.8rem 1.2rem;
                border-radius: 14px;

                background-color:
                    {msg.role === 'user'
                        ? '#2563eb'
                        : (isDarkMode
                            ? '#1e293b'
                            : '#f1f5f9')};

                color:
                    {msg.role === 'user'
                        ? 'black'
                        : (isDarkMode
                            ? '#f8fafc'
                            : '#1e293b')};

                box-shadow:
                    0 1px 2px rgba(0,0,0,0.05);
            "
        >

            <div
                style="
                    display: flex;
                    flex-direction: column;
                    gap: 0.5rem;
                "
            >

                <div>
                    {#if editingIndex === index && msg.role === 'user'}

    <div style="display:flex;flex-direction:column;gap:0.5rem;">

        <input bind:value={editedText} />

        <div style="display:flex;gap:0.5rem;">
            <button onclick={() => saveEdit(index)}>Guardar</button>
            <button onclick={cancelEdit}>Cancelar</button>
        </div>

    </div>

{:else}

    <div>{msg.text}</div>

    {#if msg.role === 'user'}
        <button onclick={() => startEdit(index)} style="background:none;border:none;cursor:pointer;">
        <Pencil size={18} />
        </button>
    {/if}

{/if}
                </div>

                {#if msg.role === 'assistant'}

                    <div
                        style="
                            display: flex;
                            gap: 0.5rem;
                            align-items: center;
                        "
                    >

                        <button onclick={() => copyMessage(msg.text, index)}>
                        {#if msg.copied}
                     <Check size={18} color="#22c55e" />
                    {:else}
                    <Copy size={18} />
                    {/if}
                    </button>

                    </div>

                {/if}

            </div>

        </div>

    </div>

{/each}
                
                {#if isAsking}
                    <div style="display: flex; justify-content: flex-start;">
                        <div style="padding: 0.8rem 1.2rem; border-radius: 14px; background-color: {isDarkMode ? '#1e293b' : '#f1f5f9'}; color: {isDarkMode ? '#94a3b8' : '#64748b'};">
                            Pensando... 🧠
                        </div>
                    </div>
                {/if}
            </div>

            <div style="padding: 1.2rem; background-color: {isDarkMode ? '#1e293b' : '#ffffff'}; border-top: 1px solid {isDarkMode ? '#334155' : '#e2e8f0'}; display: flex; gap: 0.8rem; transition: all 0.3s;">
                <input 
                    type="text" 
                    bind:value={question} 
                    onkeydown={(e) => e.key === 'Enter' && handleAsk()}
                    placeholder="Escribe tu pregunta..." 
                    style="flex: 1; padding: 0.8rem; border: 1px solid {isDarkMode ? '#475569' : '#cbd5e1'}; border-radius: 8px; outline: none; background-color: {isDarkMode ? '#334155' : '#f8fafc'}; color: {isDarkMode ? 'white' : '#1e293b'}; transition: all 0.3s;"
                    disabled={isAsking}
                />
                <button 
                    onclick={handleAsk} 
                    disabled={isAsking || !question.trim()}
                    style="background:none;border:none;cursor:pointer;">
                    <Send size={18} />
                </button>
            </div>
        </div>
    {/if}
</main>