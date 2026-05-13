<script lang="ts">
	let fileInput: HTMLInputElement | null = null;
	
	let uploadStatus = $state('');
	let documentId = $state('');
	let selectedFileName = $state('');

	// --- Nuevas variables para el Chat ---
	let question = $state('');
	let messages = $state<{role: string, text: string}[]>([]);
	let isAsking = $state(false);

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

		if (file.type !== 'application/pdf') {
			uploadStatus = '❌ El archivo debe ser un PDF válido.';
			return;
		}

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
				// Iniciamos el chat con un mensaje de bienvenida de la IA
				messages = [{ role: 'assistant', text: `¡Listo! He analizado "${selectedFileName}". ¿Qué te gustaría saber sobre este documento?` }];
			} else {
				const errorData = await response.json();
				uploadStatus = `❌ Error: ${errorData.detail || 'Fallo al procesar el PDF'}`;
			}
		} catch (error) {
			uploadStatus = '❌ Error de conexión con el backend.';
		}
	}

	async function handleAsk() {
		if (!question.trim() || isAsking) return;

		// 1. Mostramos la pregunta del usuario en el chat
		messages = [...messages, { role: 'user', text: question }];
		const currentQuestion = question;
		question = ''; // Limpiamos el input
		isAsking = true;

		try {
			// 2. Llamamos a nuestro futuro endpoint en FastAPI
			const response = await fetch('http://localhost:8000/chat', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					document_id: documentId,
					question: currentQuestion
				})
			});

			if (response.ok) {
				const data = await response.json();
				// 3. Mostramos la respuesta de la IA
				messages = [...messages, { role: 'assistant', text: data.answer }];
			} else {
				messages = [...messages, { role: 'assistant', text: '❌ Error en el servidor al generar la respuesta.' }];
			}
		} catch (error) {
			messages = [...messages, { role: 'assistant', text: '❌ Error de conexión con el backend.' }];
		} finally {
			isAsking = false;
		}
	}
</script>

<main style="max-width: 700px; margin: 3rem auto; font-family: sans-serif; display: flex; flex-direction: column; height: 80vh;">
	<h1 style="color: #333; text-align: center;">Chat con tu PDF 📄</h1>
	
	{#if !documentId}
		<!-- PANTALLA DE CARGA (Solo se ve si no hay documento) -->
		<div style="padding: 3rem 2rem; border: 2px dashed #cbd5e1; border-radius: 12px; background-color: #f8fafc; text-align: center; margin-top: 2rem;">
			<p style="color: #64748b; margin-bottom: 2rem; font-size: 1.1rem;">Sube un documento para comenzar la conversación.</p>
			
			<label style="cursor: pointer; padding: 0.75rem 1.5rem; background-color: #e2e8f0; color: #334155; border-radius: 6px; font-weight: bold; display: inline-block; transition: background 0.2s;">
				Elegir archivo PDF
				<input type="file" accept=".pdf" bind:this={fileInput} on:change={handleFileChange} style="display: none;" />
			</label>

			{#if selectedFileName}
				<div style="margin-top: 2rem;">
					<p style="margin-bottom: 1rem; color: #0f172a;">Archivo seleccionado: <strong>{selectedFileName}</strong></p>
					<button on:click={handleUpload} style="cursor: pointer; padding: 0.75rem 1.5rem; background-color: #2563eb; color: white; border: none; border-radius: 6px; font-weight: bold; font-size: 1rem;">
						Empezar Chat
					</button>
				</div>
			{/if}

			{#if uploadStatus}
				<p style="margin-top: 1.5rem; color: #475569;">{uploadStatus}</p>
			{/if}
		</div>

	{:else}
		<!-- PANTALLA DE CHAT (Se ve después de subir el PDF) -->
		<div style="flex: 1; display: flex; flex-direction: column; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; background: white; margin-top: 1rem; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);">
			
			<!-- Área de mensajes -->
			<div style="flex: 1; overflow-y: auto; padding: 1.5rem; display: flex; flex-direction: column; gap: 1rem; background-color: #f8fafc;">
				{#each messages as msg}
					<div style="display: flex; justify-content: {msg.role === 'user' ? 'flex-end' : 'flex-start'};">
						<div style="max-width: 80%; padding: 0.75rem 1.25rem; border-radius: 12px; {msg.role === 'user' ? 'background-color: #2563eb; color: white; border-bottom-right-radius: 2px;' : 'background-color: white; color: #1e293b; border: 1px solid #e2e8f0; border-bottom-left-radius: 2px; box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);'}">
							{msg.text}
						</div>
					</div>
				{/each}
				
				{#if isAsking}
					<div style="display: flex; justify-content: flex-start;">
						<div style="padding: 0.75rem 1.25rem; border-radius: 12px; background-color: white; color: #64748b; border: 1px solid #e2e8f0;">
							Pensando... 🧠
						</div>
					</div>
				{/if}
			</div>

			<!-- Input para escribir -->
			<div style="padding: 1rem; background: white; border-top: 1px solid #e2e8f0; display: flex; gap: 0.5rem;">
				<input 
					type="text" 
					bind:value={question} 
					on:keydown={(e) => e.key === 'Enter' && handleAsk()}
					placeholder="Escribe tu pregunta aquí..." 
					style="flex: 1; padding: 0.75rem; border: 1px solid #cbd5e1; border-radius: 6px; outline: none; font-size: 1rem;"
					disabled={isAsking}
				/>
				<button 
					on:click={handleAsk} 
					disabled={isAsking || !question.trim()}
					style="padding: 0.75rem 1.5rem; background-color: #2563eb; color: white; border: none; border-radius: 6px; font-weight: bold; cursor: {isAsking || !question.trim() ? 'not-allowed' : 'pointer'}; opacity: {isAsking || !question.trim() ? 0.6 : 1};"
				>
					Enviar
				</button>
			</div>
		</div>
	{/if}
</main>