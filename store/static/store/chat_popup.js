// Chat popup logic for WingfoilBot
let chatPopupVisible = false;

function toggleChatPopup() {
    chatPopupVisible = !chatPopupVisible;
    document.getElementById('chat-popup').style.display = chatPopupVisible ? 'block' : 'none';
}

function markdownToHtml(text) {
    // Solo convierte [texto](url) en enlaces HTML
    return text.replace(/\[([^\]]+)\]\(([^\)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
}

function saveChatHistory() {
    const chatBody = document.getElementById('chat-body');
    const messages = [];
    chatBody.querySelectorAll('.chat-msg').forEach(msgDiv => {
        const sender = msgDiv.classList.contains('user') ? 'user' : 'agent';
        const text = msgDiv.innerText;
        messages.push({ sender, text });
    });
    localStorage.setItem('wingfoil_chat_history', JSON.stringify(messages));
}

function loadChatHistory() {
    const history = localStorage.getItem('wingfoil_chat_history');
    if (!history) return;
    const messages = JSON.parse(history);
    messages.forEach(msg => appendMessage(msg.sender, msg.text));
}

function appendMessage(sender, text) {
    const chatBody = document.getElementById('chat-body');
    const msgDiv = document.createElement('div');
    msgDiv.className = sender === 'user' ? 'chat-msg user' : 'chat-msg agent';
    if (sender === 'agent') {
        msgDiv.innerHTML = `<span>${markdownToHtml(text)}</span>`;
    } else {
        msgDiv.innerHTML = `<span>${text}</span>`;
    }
    chatBody.appendChild(msgDiv);
    chatBody.scrollTop = chatBody.scrollHeight;
    saveChatHistory();
}

function getChatHistory() {
    const history = localStorage.getItem('wingfoil_chat_history');
    if (!history) return [];
    return JSON.parse(history);
}

function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    if (!message) {
        appendMessage('agent', 'Por favor, escribe un mensaje.');
        return;
    }
    appendMessage('user', message);
    input.value = '';
    appendMessage('agent', '<span class="typing">WingfoilBot está escribiendo...</span>');

    // Obtén el historial antes de enviar
    const history = getChatHistory();

    fetch('/chat_api/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message, history: history })
    })
    .then(async response => {
        console.log('Respuesta recibida del backend, status:', response.status);
        if (response.status === 405) {
            const text = await response.text();
            appendMessage('agent', `Método no permitido (405). El backend solo acepta POST. Respuesta: <pre>${text}</pre>`);
            return;
        }
        let data;
        try {
            console.log('Intentando parsear JSON...');
            data = await response.json();
            console.log('JSON parseado:', data);

            // Remove typing indicator
            try {
                console.log('Intentando eliminar indicador de escritura...');
                const chatBody = document.getElementById('chat-body');
                const lastMsg = chatBody.querySelector('.typing')?.parentElement;
                if (lastMsg) {
                    chatBody.removeChild(lastMsg);
                    console.log('Indicador de escritura eliminado.');
                } else {
                    console.log('No se encontró indicador de escritura para eliminar.');
                }
            } catch (domError) {
                console.error('Error eliminando indicador de escritura:', domError);
            }

            if (data && data.response) {
                console.log('Intentando añadir mensaje del agente...');
                try {
                    appendMessage('agent', data.response);
                    console.log('Mensaje del agente añadido.');
                } catch (appendError) {
                    console.error('Error añadiendo mensaje del agente:', appendError);
                    appendMessage('agent', `Error al mostrar respuesta: ${appendError}`);
                }
            } else {
                console.log('No hay data.response en el JSON.');
                appendMessage('agent', 'Sin respuesta del agente.');
            }
        } catch (e) {
            console.error('Error en el bloque try principal (parseo JSON o post-procesamiento):', e);
            // Si no es JSON, intenta mostrar el texto plano (HTML de error)
            try {
                const chatBody = document.getElementById('chat-body');
                const lastMsg = chatBody.querySelector('.typing')?.parentElement;
                if (lastMsg) chatBody.removeChild(lastMsg);
                const text = await response.text();
                appendMessage('agent', `<pre style="white-space: pre-wrap; max-width: 300px; overflow-x:auto;">Error procesando respuesta: ${e}<br>Respuesta cruda: ${text}</pre>`);
            } catch (fallbackError) {
                console.error('Error en el fallback catch:', fallbackError);
                appendMessage('agent', `Error crítico al procesar respuesta: ${fallbackError}`);
            }
        }
    })
    .catch((err) => {
        // Elimina el mensaje de escribiendo si existe
        const chatBody = document.getElementById('chat-body');
        const lastMsg = chatBody.querySelector('.typing')?.parentElement;
        if (lastMsg) chatBody.removeChild(lastMsg);
        console.error('Error en fetch/chat:', err);
        appendMessage('agent', `Lo siento, hubo un error al contactar con el agente.<br><pre>${err}</pre>`);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    loadChatHistory();
    document.getElementById('chat-toggle-btn').onclick = toggleChatPopup;
    document.getElementById('chat-send-btn').onclick = sendMessage;
    document.getElementById('chat-input').addEventListener('keydown', function(e) {
        if (e.key === 'Enter') sendMessage();
    });
});
