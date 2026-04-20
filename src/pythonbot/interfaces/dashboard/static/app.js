const API_BASE = '/api';
const WS_URL = `ws://${window.location.host}/ws/stream`;

let ws;

function initApp() {
    connectWebSocket();
    loadSkills();
    loadDoctorInfo();
    
    // Enter key para chat
    document.getElementById("chat-input").addEventListener("keypress", function(e) {
        if (e.key === "Enter") sendMessage();
    });
}

function switchView(viewName) {
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active-view'));
    document.getElementById(`view-${viewName}`).classList.add('active-view');
    
    document.querySelectorAll('.nav-links li').forEach(li => li.classList.remove('active'));
    event.currentTarget.classList.add('active');
}

function connectWebSocket() {
    ws = new WebSocket(WS_URL);
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if(data.type === 'heartbeat') {
            document.getElementById('cpu-metric').innerText = `${data.cpu}%`;
            document.querySelector('.cpu-fill').style.width = `${data.cpu}%`;
            
            document.getElementById('ram-metric').innerText = `${data.ram.toFixed(1)}%`;
            document.querySelector('.ram-fill').style.width = `${data.ram}%`;
            
            document.getElementById('token-metric').innerText = data.tokens;
            document.getElementById('active-session-id').innerText = data.active_session;
        }
    };
    
    ws.onclose = () => {
        setTimeout(connectWebSocket, 3000); // Reconnect
    };
}

async function loadSkills() {
    try {
        const res = await fetch(`${API_BASE}/skills`);
        const skills = await res.json();
        
        const container = document.getElementById('skills-container');
        if (skills.length === 0) {
            container.innerHTML = `<div class="glass-card full-width text-center">Nenhuma skill encontrada em /data/skills</div>`;
            return;
        }
        
        container.innerHTML = '';
        skills.forEach(s => {
            container.innerHTML += `
                <div class="glass-card">
                    <h3><i class="fa-solid fa-bolt" style="color:var(--accent)"></i> ${s.name}</h3>
                    <p style="color:var(--text-muted); margin: 10px 0; font-size: 0.9rem;">${s.description}</p>
                    <span class="badget">${s.steps ? s.steps.length : 0} steps</span>
                </div>
            `;
        });
    } catch(e) {
        console.error(e);
    }
}

async function loadDoctorInfo() {
    try {
        const res = await fetch(`${API_BASE}/status`);
        const data = await res.json();
        
        const container = document.getElementById('doctor-container');
        container.innerHTML = `<h3 style="margin-bottom: 20px;">Health Check</h3>`;
        
        for (const [key, value] of Object.entries(data.doctor)) {
            let icon = value.status === 'ok' ? '<i class="fa-solid fa-check status-ok"></i>' : '<i class="fa-solid fa-xmark status-error"></i>';
            if(value.status === 'warning') icon = '<i class="fa-solid fa-triangle-exclamation status-info"></i>';
            
            container.innerHTML += `
               <div style="padding: 10px; border-bottom: 1px solid var(--border-glass); display:flex; gap:10px;">
                    ${icon} <strong>${key.toUpperCase()}</strong>: <span>${value.msg}</span>
               </div>
            `;
        }
    } catch(e) {
        console.error(e);
    }
}

async function sendMessage() {
    const input = document.getElementById("chat-input");
    const text = input.value.trim();
    if(!text) return;
    
    const messages = document.getElementById("chat-messages");
    
    // Add user message
    messages.innerHTML += `<div class="msg user-msg">${text}</div>`;
    input.value = "";
    messages.scrollTop = messages.scrollHeight;
    
    try {
        const res = await fetch(`${API_BASE}/message`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message: text})
        });
        const data = await res.json();
        
        messages.innerHTML += `<div class="msg bot-msg">${data.response}</div>`;
        messages.scrollTop = messages.scrollHeight;
    } catch (e) {
        messages.innerHTML += `<div class="msg bot-msg" style="color: #f43f5e">Erro de conexão API.</div>`;
    }
}

// Initializa
document.addEventListener('DOMContentLoaded', initApp);
