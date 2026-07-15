// Qyverion - Frontend Interactions & Dynamic Log Ingestion

function bootstrapApp() {
    initCanvas();
    initBootLogs();
    initInteractivity();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bootstrapApp);
} else {
    bootstrapApp();
}

// 1. Canvas Node-Grid Visualization
function initCanvas() {
    const canvas = document.getElementById('cyber-grid');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    let width = canvas.width = window.innerWidth;
    let height = canvas.height = window.innerHeight;
    
    const nodes = [];
    const maxNodes = 60;
    const connectionDist = 120;
    
    class Node {
        constructor() {
            this.x = Math.random() * width;
            this.y = Math.random() * height;
            this.vx = (Math.random() - 0.5) * 0.4;
            this.vy = (Math.random() - 0.5) * 0.4;
            this.radius = Math.random() * 2 + 1;
            this.pulseRate = Math.random() * 0.02 + 0.01;
            this.pulseVal = Math.random();
        }
        
        update() {
            this.x += this.vx;
            this.y += this.vy;
            
            // Bounds check
            if (this.x < 0 || this.x > width) this.vx *= -1;
            if (this.y < 0 || this.y > height) this.vy *= -1;
            
            this.pulseVal += this.pulseRate;
            if (this.pulseVal > Math.PI * 2) this.pulseVal = 0;
        }
        
        draw() {
            ctx.beginPath();
            const alpha = 0.3 + Math.sin(this.pulseVal) * 0.2;
            ctx.arc(this.x, this.y, this.radius + Math.sin(this.pulseVal) * 0.5, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(0, 242, 254, ${alpha})`;
            ctx.fill();
        }
    }
    
    // Create initial nodes
    for (let i = 0; i < maxNodes; i++) {
        nodes.push(new Node());
    }
    
    function animate() {
        ctx.clearRect(0, 0, width, height);
        
        // Draw grid lines
        ctx.strokeStyle = 'rgba(0, 242, 254, 0.02)';
        ctx.lineWidth = 1;
        const gridSize = 80;
        for (let x = 0; x < width; x += gridSize) {
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, height);
            ctx.stroke();
        }
        for (let y = 0; y < height; y += gridSize) {
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(width, y);
            ctx.stroke();
        }
        
        // Update & Draw nodes
        nodes.forEach(node => {
            node.update();
            node.draw();
        });
        
        // Connect nodes
        for (let i = 0; i < nodes.length; i++) {
            for (let j = i + 1; j < nodes.length; j++) {
                const dist = Math.hypot(nodes[i].x - nodes[j].x, nodes[i].y - nodes[j].y);
                if (dist < connectionDist) {
                    ctx.beginPath();
                    ctx.moveTo(nodes[i].x, nodes[i].y);
                    ctx.lineTo(nodes[j].x, nodes[j].y);
                    const alpha = (1 - dist / connectionDist) * 0.12;
                    ctx.strokeStyle = `rgba(0, 242, 254, ${alpha})`;
                    ctx.lineWidth = 0.8;
                    ctx.stroke();
                }
            }
        }
        
        requestAnimationFrame(animate);
    }
    
    animate();
    
    // Resize handler
    window.addEventListener('resize', () => {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    });
}

// 2. Mock System Bootlog Streaming (Visual Polish)
const MOCK_LOGS = [
    { type: 'info', tag: 'SYS', msg: 'Initializing Qyverion Platform Foundation...' },
    { type: 'info', tag: 'ENV', msg: 'Loading environment variables from root .env configuration...' },
    { type: 'success', tag: 'ENV', msg: 'Config module compiled successfully. Strict type validation loaded.' },
    { type: 'info', tag: 'DB', msg: 'Establishing connection to PostgreSQL at localhost:5432/qyverion...' },
    { type: 'success', tag: 'DB', msg: 'SQLAlchemy database engine instantiated. Connection pool mapping online.' },
    { type: 'success', tag: 'ORM', msg: 'SQLAlchemy declarative base mappings registered.' },
    { type: 'info', tag: 'ALB', msg: 'Initializing Alembic database migrations framework...' },
    { type: 'success', tag: 'ALB', msg: 'Alembic configuration initialized. Target metadata bound.' },
    { type: 'info', tag: 'APP', msg: 'Constructing FastAPI core application middleware layers...' },
    { type: 'success', tag: 'APP', msg: 'CORS policy configured. Static assets serving routing established.' },
    { type: 'success', tag: 'SYS', msg: 'All clean architecture core domains verified. Application bootstrap ready.' },
    { type: 'warning', tag: 'SEC', msg: 'Warning: Running in development mode. Secrets stored locally.' },
    { type: 'success', tag: 'SYS', msg: 'Uvicorn server listening on http://127.0.0.1:8000 (Ctrl+C to stop)' }
];

function initBootLogs() {
    const container = document.getElementById('boot-log-container');
    const clearBtn = document.getElementById('clear-logs');
    if (!container) return;
    
    let logIndex = 0;
    
    function addLogLine() {
        if (logIndex >= MOCK_LOGS.length) return;
        
        const log = MOCK_LOGS[logIndex];
        const line = document.createElement('div');
        line.className = `log-line log-${log.type}`;
        
        const timeSpan = document.createElement('span');
        timeSpan.className = 'log-time';
        const now = new Date();
        timeSpan.textContent = now.toISOString().split('T')[1].slice(0, -1);
        
        const tagSpan = document.createElement('span');
        tagSpan.className = 'log-tag';
        tagSpan.textContent = `[${log.tag}]`;
        
        const msgSpan = document.createElement('span');
        msgSpan.className = 'log-msg';
        msgSpan.textContent = log.msg;
        
        line.appendChild(timeSpan);
        line.appendChild(tagSpan);
        line.appendChild(msgSpan);
        
        container.appendChild(line);
        container.scrollTop = container.scrollHeight;
        
        logIndex++;
        
        // Random slight delays
        setTimeout(addLogLine, Math.random() * 500 + 200);
    }
    
    addLogLine();
    
    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            container.innerHTML = '';
            logIndex = 0;
            addLogLine();
        });
    }
}

// // 3. Tab Navigation & Live API Interactivity
function initInteractivity() {
    const navOverview = document.getElementById('nav-overview');
    const navIngestion = document.getElementById('nav-ingestion');
    const navDetection = document.getElementById('nav-detection');
    const navAICopilot = document.getElementById('nav-ai-copilot');
    
    const tabOverview = document.getElementById('tab-overview');
    const tabIngestion = document.getElementById('tab-ingestion');
    const tabDetection = document.getElementById('tab-detection');
    const tabAICopilot = document.getElementById('tab-ai-copilot');

    if (!navOverview || !navIngestion || !navDetection || !navAICopilot) return;

    function resetTabs() {
        [navOverview, navIngestion, navDetection, navAICopilot].forEach(nav => nav.classList.remove('active'));
        [tabOverview, tabIngestion, tabDetection, tabAICopilot].forEach(tab => tab.classList.add('hidden'));
    }

    navOverview.addEventListener('click', (e) => {
        e.preventDefault();
        resetTabs();
        navOverview.classList.add('active');
        tabOverview.classList.remove('hidden');
    });

    navIngestion.addEventListener('click', (e) => {
        e.preventDefault();
        resetTabs();
        navIngestion.classList.add('active');
        tabIngestion.classList.remove('hidden');
        fetchDBLogs();
    });

    navDetection.addEventListener('click', (e) => {
        e.preventDefault();
        resetTabs();
        navDetection.classList.add('active');
        tabDetection.classList.remove('hidden');
        fetchDBAlerts();
    });

    navAICopilot.addEventListener('click', (e) => {
        e.preventDefault();
        resetTabs();
        navAICopilot.classList.add('active');
        tabAICopilot.classList.remove('hidden');
        loadCopilotAlerts();
    });

    // Ingestion Form Submit handler
    const ingestForm = document.getElementById('ingest-form');
    const submitResult = document.getElementById('submit-result');
    
    if (ingestForm) {
        ingestForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const rawData = document.getElementById('ingest-raw-data').value.trim();
            const logSource = document.getElementById('ingest-log-source').value;
            
            if (!rawData) {
                alert('Please enter a raw log message before submitting.');
                return;
            }
            
            submitResult.classList.remove('hidden');
            submitResult.innerHTML = '<span class="text-cyber-accent">Sending payload to database ingestion pipeline...</span>';
            
            try {
                const response = await fetch('/api/v1/logs/ingest', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        raw_data: rawData,
                        log_source: logSource,
                        severity: 'INFO', // Re-evaluated dynamically by backend services
                        event_timestamp: new Date().toISOString()
                    })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    const sevClass = data.severity === 'CRITICAL' ? 'badge-crit' : (data.severity === 'WARNING' ? 'badge-warn' : 'badge-info');
                    submitResult.innerHTML = `
                        <span class="text-cyber-success">[PIPELINE SUCCESS] Record Ingested:</span><br>
                        ID: <span class="text-cyber-light">${data.id}</span><br>
                        Source: <span class="text-cyber-light">${data.log_source}</span><br>
                        Severity: <span class="badge ${sevClass}">${data.severity}</span><br>
                        Extracted Source IP: <span class="text-cyber-light">${data.source_ip || 'None detected'}</span><br>
                        Extracted Dest IP:   <span class="text-cyber-light">${data.destination_ip || 'None detected'}</span><br>
                        Ingested At: <span class="text-cyber-muted">${new Date(data.ingested_at).toLocaleTimeString()}</span>
                    `;
                    
                    // Clear the inputs
                    document.getElementById('ingest-raw-data').value = '';
                    
                    // Refresh list registry table
                    fetchDBLogs();
                } else {
                    submitResult.innerHTML = `<span class="text-cyber-danger">[ERROR] Ingestion Rejected: ${data.detail || 'Malformed payload syntax'}</span>`;
                }
            } catch (err) {
                submitResult.innerHTML = `<span class="text-cyber-danger">[ERROR] Server connection error: ${err.message}</span>`;
            }
        });
    }

    // Refresh button listeners
    const refreshBtn = document.getElementById('refresh-logs-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            fetchDBLogs();
        });
    }

    const refreshAlertsBtn = document.getElementById('refresh-alerts-btn');
    if (refreshAlertsBtn) {
        refreshAlertsBtn.addEventListener('click', () => {
            fetchDBAlerts();
        });
    }

    // AI Copilot Chat Form handler
    const chatForm = document.getElementById('chat-input-form');
    if (chatForm) {
        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const messageInput = document.getElementById('chat-user-message');
            const messageText = messageInput.value.trim();
            if (!messageText) return;

            messageInput.value = '';
            appendChatMessage('user', messageText);

            // Add placeholder loading bubble
            const loadingId = appendChatMessage('assistant', `
                <div class="flex items-center gap-3 animate-pulse">
                    <svg class="animate-spin h-4 w-4 text-cyber-accent" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span class="text-cyber-muted italic">Consulting local Llama3.2 model...</span>
                </div>
            `);

            try {
                const response = await fetch('/api/v1/ai/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        message: messageText
                    })
                });

                const data = await response.json();
                removeChatMessage(loadingId);

                if (response.ok) {
                    appendChatMessage('assistant', data.reply);
                } else {
                    appendChatMessage('assistant', `<span class="text-cyber-danger">[Error] Copilot rejected request: ${data.detail || 'Malformed payload'}</span>`);
                }
            } catch (err) {
                removeChatMessage(loadingId);
                appendChatMessage('assistant', `<span class="text-cyber-danger">[Error] Remote socket closed: ${err.message}</span>`);
            }
        });
    }

    // Clear chat console handler
    const clearChatBtn = document.getElementById('clear-chat-btn');
    if (clearChatBtn) {
        clearChatBtn.addEventListener('click', () => {
            const container = document.getElementById('chat-messages-container');
            if (container) {
                container.innerHTML = `
                    <div class="message assistant flex gap-3 p-3 bg-cyber-accent/5 border border-cyber-accent/15 rounded animate-fade-in">
                        <div class="font-bold text-cyber-accent">AI:</div>
                        <div class="text-cyber-light flex-1 leading-relaxed">
                            Console reset. Ready to inspect threat parameters, analyze logs, or construct response playbooks.
                        </div>
                    </div>
                `;
            }
        });
    }
}

async function fetchDBLogs() {
    const tbody = document.getElementById('db-logs-tbody');
    const refreshIcon = document.getElementById('refresh-icon');
    if (!tbody) return;

    if (refreshIcon) refreshIcon.classList.add('animate-spin');

    try {
        const response = await fetch('/api/v1/logs/');
        const logs = await response.json();
        
        if (response.ok) {
            if (logs.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="5" class="text-center font-mono text-xs text-cyber-muted py-8">
                            No logs found in the database. Ingest a raw event to get started.
                        </td>
                    </tr>
                `;
            } else {
                tbody.innerHTML = logs.map(log => {
                    const sevClass = log.severity === 'CRITICAL' ? 'badge-crit' : (log.severity === 'WARNING' ? 'badge-warn' : 'badge-info');
                    const formattedDate = new Date(log.ingested_at).toLocaleString();
                    const escapedRaw = log.raw_data.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
                    const truncatedRaw = escapedRaw.length > 55 ? escapedRaw.substring(0, 55) + '...' : escapedRaw;
                    
                    return `
                        <tr class="border-b border-cyber-border/40 font-mono text-xs">
                            <td class="text-cyber-muted whitespace-nowrap">${formattedDate}</td>
                            <td class="text-cyber-light font-semibold">${log.log_source}</td>
                            <td><span class="badge ${sevClass}">${log.severity}</span></td>
                            <td class="text-cyber-accent">${log.source_ip || 'N/A'}</td>
                            <td class="text-cyber-muted max-w-xs truncate" title="${escapedRaw}">${truncatedRaw}</td>
                        </tr>
                    `;
                }).join('');
            }
        } else {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center font-mono text-xs text-cyber-danger py-8">
                        [HTTP Error] Failed to retrieve parsed records.
                    </td>
                </tr>
            `;
        }
    } catch (err) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center font-mono text-xs text-cyber-danger py-8">
                    [Network Error] Connection refused: ${err.message}
                </td>
            </tr>
        `;
    } finally {
        if (refreshIcon) {
            setTimeout(() => {
                refreshIcon.classList.remove('animate-spin');
            }, 500);
        }
    }
}

async function fetchDBAlerts() {
    const tbody = document.getElementById('db-alerts-tbody');
    const refreshIcon = document.getElementById('refresh-alerts-icon');
    if (!tbody) return;

    if (refreshIcon) refreshIcon.classList.add('animate-spin');

    try {
        const response = await fetch('/api/v1/alerts/');
        const alerts = await response.json();
        
        if (response.ok) {
            if (alerts.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="6" class="text-center font-mono text-xs text-cyber-muted py-8">
                            No active security incidents found. System metrics nominal.
                        </td>
                    </tr>
                `;
            } else {
                tbody.innerHTML = alerts.map(alert => {
                    const isNew = alert.status === 'NEW';
                    const sevClass = alert.severity === 'CRITICAL' ? 'badge-crit' : (alert.severity === 'WARNING' || alert.severity === 'HIGH' ? 'badge-warn' : 'badge-info');
                    const statusClass = alert.status === 'NEW' ? 'badge-crit' : (alert.status === 'RESOLVED' ? 'badge-info' : 'badge-warn');
                    const formattedDate = new Date(alert.created_at).toLocaleString();
                    
                    const actionButton = isNew 
                        ? `<button onclick="resolveAlert(${alert.id})" class="cyber-btn secondary py-0.5 px-2 text-[10px]">RESOLVE</button>`
                        : `<span class="text-cyber-muted">-</span>`;
                        
                    return `
                        <tr class="border-b border-cyber-border/40 font-mono text-xs text-left">
                            <td class="text-cyber-muted whitespace-nowrap">${formattedDate}</td>
                            <td class="text-cyber-light font-bold">${alert.title}</td>
                            <td class="text-cyber-muted max-w-sm truncate" title="${alert.description}">${alert.description}</td>
                            <td><span class="badge ${sevClass}">${alert.severity}</span></td>
                            <td><span class="badge ${statusClass}">${alert.status}</span></td>
                            <td>${actionButton}</td>
                        </tr>
                    `;
                }).join('');
            }
        } else {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center font-mono text-xs text-cyber-danger py-8">
                        [HTTP Error] Failed to retrieve incident queue.
                    </td>
                </tr>
            `;
        }
    } catch (err) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center font-mono text-xs text-cyber-danger py-8">
                    [Network Error] Connection refused: ${err.message}
                </td>
            </tr>
        `;
    } finally {
        if (refreshIcon) {
            setTimeout(() => {
                refreshIcon.classList.remove('animate-spin');
            }, 500);
        }
    }
}

// Global resolve alert utility function
window.resolveAlert = async function(alertId) {
    try {
        const response = await fetch(`/api/v1/alerts/${alertId}/status`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                status: 'RESOLVED'
            })
        });
        
        if (response.ok) {
            fetchDBAlerts();
        } else {
            alert('Failed to update alert state on remote server.');
        }
    } catch (err) {
        alert(`Error communicating with backend: ${err.message}`);
    }
};

// AI Copilot Helpers
async function loadCopilotAlerts() {
    const listContainer = document.getElementById('copilot-alerts-list');
    if (!listContainer) return;

    try {
        const response = await fetch('/api/v1/alerts/');
        const alerts = await response.json();

        if (response.ok) {
            const activeAlerts = alerts.filter(a => a.status === 'NEW');
            if (activeAlerts.length === 0) {
                listContainer.innerHTML = '<span class="text-[10px] text-cyber-muted font-mono py-2 text-center">No active alerts available.</span>';
            } else {
                listContainer.innerHTML = activeAlerts.map(alert => `
                    <div class="flex flex-col gap-1.5 p-2 bg-cyber-dark/40 border border-cyber-border/40 rounded">
                        <span class="text-[9px] text-cyber-muted">${new Date(alert.created_at).toLocaleTimeString()}</span>
                        <span class="text-[10px] text-cyber-light font-bold truncate" title="${alert.title}">${alert.title}</span>
                        <button onclick="generatePlaybookFor(${alert.id})" class="cyber-btn secondary py-1 text-[9px] w-full text-center mt-1">
                            GENERATE PLAYBOOK
                        </button>
                    </div>
                `).join('');
            }
        }
    } catch (err) {
        listContainer.innerHTML = '<span class="text-[10px] text-cyber-danger font-mono py-2 text-center">Failed to fetch alerts list.</span>';
    }
}

async function generatePlaybookFor(alertId) {
    appendChatMessage('user', `Generate incident response playbook for Alert ID #${alertId}`);
    
    // Add placeholder loading bubble
    const loadingId = appendChatMessage('assistant', `
        <div class="flex items-center gap-3 animate-pulse p-1">
            <svg class="animate-spin h-5 w-5 text-cyber-accent" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <div class="flex-1 font-mono text-xs">
                <span class="text-cyber-accent font-bold">ANALYZING THREAT CORRELATION DATA...</span><br>
                <span class="text-cyber-muted text-[10px]">Constructing step-by-step mitigation playbook for incident ID ${alertId}</span>
            </div>
        </div>
    `);

    try {
        const response = await fetch(`/api/v1/ai/playbook/${alertId}`, {
            method: 'POST'
        });
        const data = await response.json();
        removeChatMessage(loadingId);

        if (response.ok) {
            appendChatMessage('assistant', data.reply);
        } else {
            appendChatMessage('assistant', `<span class="text-cyber-danger">[Error] Failed to generate playbook: ${data.detail}</span>`);
        }
    } catch (err) {
        removeChatMessage(loadingId);
        appendChatMessage('assistant', `<span class="text-cyber-danger">[Error] Socket connection reset: ${err.message}</span>`);
    }
}

// Global quick actions caller
window.sendCopilotSuggested = function(text) {
    const input = document.getElementById('chat-user-message');
    if (input) {
        input.value = text;
        const form = document.getElementById('chat-input-form');
        if (form) {
            form.dispatchEvent(new Event('submit'));
        }
    }
};
window.generatePlaybookFor = generatePlaybookFor;

function appendChatMessage(sender, text) {
    const container = document.getElementById('chat-messages-container');
    if (!container) return "";
    
    const messageId = "chat-msg-" + Date.now() + Math.random().toString(36).substr(2, 5);
    const bubbleClass = sender === 'user' 
        ? 'bg-cyber-light/5 border-cyber-border/20' 
        : 'bg-cyber-accent/5 border-cyber-accent/15';
    
    const senderLabel = sender === 'user' 
        ? '<div class="font-bold text-cyber-light">USER:</div>' 
        : '<div class="font-bold text-cyber-accent">AI:</div>';
        
    const isHtml = text.trim().startsWith('<') && text.trim().endsWith('>');
    const formattedBody = sender === 'user' ? text : (isHtml ? text : formatMarkdown(text));

    container.innerHTML += `
        <div id="${messageId}" class="message ${sender} flex gap-3 p-3 border rounded animate-fade-in ${bubbleClass}">
            ${senderLabel}
            <div class="text-cyber-light flex-1 leading-relaxed">${formattedBody}</div>
        </div>
    `;

    // Auto-scroll terminal to bottom
    container.scrollTop = container.scrollHeight;
    
    return messageId;
}

function removeChatMessage(messageId) {
    const el = document.getElementById(messageId);
    if (el) el.remove();
}

function formatMarkdown(text) {
    if (!text) return "";
    
    // Simple HTML sanitizer/escaping to prevent breaking UI tags
    let html = text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");

    // Code blocks: ```code ... ```
    html = html.replace(/```(?:[a-zA-Z0-9]+)?\n([\s\S]*?)```/g, (match, p1) => {
        return `<pre class="bg-cyber-dark border border-cyber-border/40 p-3 rounded font-mono text-[11px] text-cyber-accent my-2 overflow-x-auto select-text">${p1.trim()}</pre>`;
    });

    // Inline code: `code`
    html = html.replace(/`([^`]+)`/g, '<code class="bg-cyber-dark/60 text-cyber-accent px-1.5 py-0.5 rounded font-mono text-[10px]">$1</code>');

    // Bold: **text**
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong class="text-cyber-light font-bold">$1</strong>');

    // Headings: #, ##, ###
    html = html.replace(/^### (.*$)/gim, '<h4 class="text-xs font-bold text-cyber-light mt-3 border-b border-cyber-border/20 pb-1 mb-1">$1</h4>');
    html = html.replace(/^## (.*$)/gim, '<h3 class="text-sm font-bold text-cyber-light mt-4 border-b border-cyber-border/30 pb-1 mb-1">$1</h3>');
    html = html.replace(/^# (.*$)/gim, '<h2 class="text-md font-bold text-cyber-accent mt-5 border-b border-cyber-border/40 pb-1 mb-1">$1</h2>');

    // Bullet points: - item
    html = html.replace(/^\s*-\s+(.*$)/gim, '<li class="list-disc list-inside text-cyber-muted ml-2 py-0.5">$1</li>');

    // Newlines replacement outside code pre blocks
    const parts = html.split(/(<pre[\s\S]*?<\/pre>)/g);
    for (let i = 0; i < parts.length; i++) {
        if (!parts[i].startsWith('<pre')) {
            parts[i] = parts[i].replace(/\n/g, '<br>');
        }
    }
    return parts.join('');
}
