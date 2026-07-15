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
    const navInvestigation = document.getElementById('nav-investigation');
    const navAICopilot = document.getElementById('nav-ai-copilot');
    const navIndicators = document.getElementById('nav-indicators');
    
    const tabOverview = document.getElementById('tab-overview');
    const tabIngestion = document.getElementById('tab-ingestion');
    const tabDetection = document.getElementById('tab-detection');
    const tabInvestigation = document.getElementById('tab-investigation');
    const tabAICopilot = document.getElementById('tab-ai-copilot');
    const tabIndicators = document.getElementById('tab-indicators');

    if (!navOverview || !navIngestion || !navDetection || !navInvestigation || !navAICopilot || !navIndicators) return;

    function resetTabs() {
        [navOverview, navIngestion, navDetection, navInvestigation, navAICopilot, navIndicators].forEach(nav => nav.classList.remove('active'));
        [tabOverview, tabIngestion, tabDetection, tabInvestigation, tabAICopilot, tabIndicators].forEach(tab => tab.classList.add('hidden'));
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

    navInvestigation.addEventListener('click', (e) => {
        e.preventDefault();
        resetTabs();
        navInvestigation.classList.add('active');
        tabInvestigation.classList.remove('hidden');
        initInvestigationGraph();
    });

    navAICopilot.addEventListener('click', (e) => {
        e.preventDefault();
        resetTabs();
        navAICopilot.classList.add('active');
        tabAICopilot.classList.remove('hidden');
        loadCopilotAlerts();
    });

    navIndicators.addEventListener('click', (e) => {
        e.preventDefault();
        resetTabs();
        navIndicators.classList.add('active');
        tabIndicators.classList.remove('hidden');
        fetchIndicatorsCatalog();
        fetchBlockedRegistry();
    });

    // Ingest Log Submit Handler
    const ingestForm = document.getElementById('ingest-form');
    if (ingestForm) {
        ingestForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const textarea = document.getElementById('ingest-raw-data');
            const resultMsg = document.getElementById('ingest-result-msg');
            const rawData = textarea.value.trim();

            if (!rawData) {
                alert('Please enter a raw log payload to submit.');
                return;
            }

            try {
                const response = await fetch('/api/v1/logs/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ raw_payload: rawData })
                });

                const data = await response.json();
                if (response.ok) {
                    resultMsg.className = "text-xs font-mono text-cyber-success block mt-2 animate-fade-in";
                    resultMsg.innerText = `[SUCCESS] Ingested Log ID #${data.id}. Detected Source: ${data.source_ip || 'None'} / Rule: ${data.log_source || 'Unknown'}`;
                    textarea.value = '';
                    fetchDBLogs();
                    
                    // Trigger Live Map Arc
                    if (data.source_ip) {
                        triggerAttackArc(data.source_ip);
                    }
                } else {
                    resultMsg.className = "text-xs font-mono text-cyber-danger block mt-2 animate-fade-in";
                    resultMsg.innerText = `[ERROR] Ingestion Rejected: ${data.detail}`;
                }
            } catch (err) {
                resultMsg.className = "text-xs font-mono text-cyber-danger block mt-2 animate-fade-in";
                resultMsg.innerText = `[ERROR] Network fault: ${err.message}`;
            }
        });
    }

    // Refresh buttons
    const refreshBtn = document.getElementById('refresh-logs-btn');
    if (refreshBtn) refreshBtn.addEventListener('click', fetchDBLogs);

    const refreshAlertsBtn = document.getElementById('refresh-alerts-btn');
    if (refreshAlertsBtn) refreshAlertsBtn.addEventListener('click', fetchDBAlerts);

    const refreshIndicatorsBtn = document.getElementById('refresh-indicators-btn');
    if (refreshIndicatorsBtn) refreshIndicatorsBtn.addEventListener('click', fetchIndicatorsCatalog);

    // AI Copilot Chat Submit Handler
    const chatForm = document.getElementById('chat-input-form');
    if (chatForm) {
        chatForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const messageInput = document.getElementById('chat-user-message');
            const messageText = messageInput.value.trim();
            if (!messageText) return;

            messageInput.value = '';
            appendChatMessage('user', messageText);

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
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: messageText })
                });

                const data = await response.json();
                removeChatMessage(loadingId);

                if (response.ok) {
                    appendChatMessage('assistant', data.reply);
                } else {
                    appendChatMessage('assistant', `<span class="text-cyber-danger">[Error] Copilot rejected request: ${data.detail}</span>`);
                }
            } catch (err) {
                removeChatMessage(loadingId);
                appendChatMessage('assistant', `<span class="text-cyber-danger">[Error] socket error: ${err.message}</span>`);
            }
        });
    }

    // Clear chat handler
    const clearChatBtn = document.getElementById('clear-chat-btn');
    if (clearChatBtn) {
        clearChatBtn.addEventListener('click', () => {
            const container = document.getElementById('chat-messages-container');
            if (container) {
                container.innerHTML = `
                    <div class="message assistant flex gap-3 p-3 bg-cyber-accent/5 border border-cyber-accent/15 rounded">
                        <div class="font-bold text-cyber-accent">AI:</div>
                        <div class="text-cyber-light flex-1 leading-relaxed">
                            Greetings, Operator. I am Qyverion AI Copilot, your local AI Security Analyst. I am ready to inspect logs, analyze security incidents, or generate mitigation playbooks. What threat vector shall we investigate?
                        </div>
                    </div>
                `;
            }
        });
    }

    // Forensic search submit handler
    const investigateForm = document.getElementById('investigate-form');
    if (investigateForm) {
        investigateForm.addEventListener('submit', (e) => {
            e.preventDefault();
            initInvestigationGraph();
        });
    }

    const resetGraphBtn = document.getElementById('reset-graph-btn');
    if (resetGraphBtn) {
        resetGraphBtn.addEventListener('click', () => {
            initInvestigationGraph();
        });
    }

    // Sync Threat Intelligence Feeds handler
    const syncFeedsBtn = document.getElementById('sync-feeds-btn');
    if (syncFeedsBtn) {
        syncFeedsBtn.addEventListener('click', async () => {
            const icon = document.getElementById('sync-feeds-icon');
            const resultBox = document.getElementById('sync-result');
            
            if (icon) icon.classList.add('animate-spin');
            resultBox.classList.add('hidden');

            try {
                const response = await fetch('/api/v1/indicators/sync', { method: 'POST' });
                const data = await response.json();
                if (response.ok) {
                    resultBox.className = "text-[10px] font-mono text-cyber-success block bg-cyber-success/5 border border-cyber-success/20 p-2 rounded mt-2 animate-fade-in";
                    resultBox.innerText = data.message;
                    fetchIndicatorsCatalog();
                } else {
                    resultBox.className = "text-[10px] font-mono text-cyber-danger block bg-cyber-danger/5 border border-cyber-danger/20 p-2 rounded mt-2 animate-fade-in";
                    resultBox.innerText = `Failed to sync: ${data.detail}`;
                }
            } catch (err) {
                resultBox.className = "text-[10px] font-mono text-cyber-danger block bg-cyber-danger/5 border border-cyber-danger/20 p-2 rounded mt-2";
                resultBox.innerText = `Sync error: ${err.message}`;
            } finally {
                if (icon) icon.classList.remove('animate-spin');
            }
        });
    }

    // Submit Custom Indicator handler
    const indicatorForm = document.getElementById('indicator-form');
    if (indicatorForm) {
        indicatorForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const valInput = document.getElementById('ind-value');
            const typeInput = document.getElementById('ind-type');
            const scoreInput = document.getElementById('ind-score');
            const descInput = document.getElementById('ind-desc');
            const resultBox = document.getElementById('indicator-result');

            resultBox.classList.add('hidden');

            try {
                const response = await fetch('/api/v1/indicators/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        indicator_value: valInput.value.trim(),
                        indicator_type: typeInput.value,
                        risk_score: parseInt(scoreInput.value),
                        description: descInput.value.trim(),
                        threat_actor: "Manual Override"
                    })
                });

                const data = await response.json();
                if (response.ok) {
                    resultBox.className = "text-[10px] font-mono text-cyber-success block mt-2 animate-fade-in";
                    resultBox.innerText = `Indicator ${data.indicator_value} registered successfully.`;
                    valInput.value = '';
                    descInput.value = '';
                    fetchIndicatorsCatalog();
                } else {
                    resultBox.className = "text-[10px] font-mono text-cyber-danger block mt-2 animate-fade-in";
                    resultBox.innerText = `Registration failed: ${data.detail}`;
                }
            } catch (err) {
                resultBox.className = "text-[10px] font-mono text-cyber-danger block mt-2";
                resultBox.innerText = `Network fault: ${err.message}`;
            }
        });
    }
}

// 4. Live Cyber Attack Map Canvas Loop
let activeMapArcs = [];

function initAttackMap() {
    const canvas = document.getElementById('attack-map-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    function resizeCanvas() {
        if (!canvas) return;
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = canvas.parentElement.clientHeight;
    }
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    
    const sfLat = 37.7749;
    const sfLon = -122.4194;
    
    function getXY(lat, lon) {
        const x = (lon + 180) * (canvas.width / 360);
        const y = (90 - lat) * (canvas.height / 180);
        return { x, y };
    }
    
    const continents = [
        [ {lat: 70, lon: -160}, {lat: 70, lon: -60}, {lat: 15, lon: -90}, {lat: 7, lon: -80}, {lat: 20, lon: -110} ],
        [ {lat: 7, lon: -80}, {lat: -5, lon: -35}, {lat: -55, lon: -70}, {lat: -20, lon: -75} ],
        [ {lat: 70, lon: 10}, {lat: 75, lon: 170}, {lat: 35, lon: 140}, {lat: 10, lon: 110}, {lat: 15, lon: 75}, {lat: 30, lon: 35}, {lat: 40, lon: -10} ],
        [ {lat: 35, lon: -10}, {lat: 30, lon: 32}, {lat: 10, lon: 45}, {lat: -34, lon: 20}, {lat: -15, lon: 12}, {lat: 5, lon: -10} ],
        [ {lat: -20, lon: 115}, {lat: -15, lon: 145}, {lat: -35, lon: 150}, {lat: -35, lon: 117} ]
    ];
    
    function drawMapBackground() {
        ctx.fillStyle = '#060a13';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.strokeStyle = 'rgba(0, 242, 254, 0.03)';
        ctx.lineWidth = 1;
        const gridSize = 40;
        for (let x = 0; x < canvas.width; x += gridSize) {
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, canvas.height);
            ctx.stroke();
        }
        for (let y = 0; y < canvas.height; y += gridSize) {
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(canvas.width, y);
            ctx.stroke();
        }
        
        ctx.fillStyle = 'rgba(0, 242, 254, 0.015)';
        ctx.strokeStyle = 'rgba(0, 242, 254, 0.12)';
        ctx.lineWidth = 1.2;
        continents.forEach(poly => {
            ctx.beginPath();
            poly.forEach((pt, idx) => {
                const xy = getXY(pt.lat, pt.lon);
                if (idx === 0) ctx.moveTo(xy.x, xy.y);
                else ctx.lineTo(xy.x, xy.y);
            });
            ctx.closePath();
            ctx.fill();
            ctx.stroke();
        });
    }
    
    let ringRadius = 0;
    
    function animate() {
        if (!canvas) return;
        drawMapBackground();
        
        const targetXY = getXY(sfLat, sfLon);
        ctx.fillStyle = '#00f2fe';
        ctx.beginPath();
        ctx.arc(targetXY.x, targetXY.y, 4, 0, Math.PI * 2);
        ctx.fill();
        
        ringRadius = (ringRadius + 0.3) % 20;
        ctx.strokeStyle = `rgba(0, 242, 254, ${1 - ringRadius/20})`;
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.arc(targetXY.x, targetXY.y, ringRadius, 0, Math.PI * 2);
        ctx.stroke();
        
        const now = Date.now();
        activeMapArcs = activeMapArcs.filter(arc => now - arc.startTime < arc.duration);
        
        activeMapArcs.forEach(arc => {
            const startXY = getXY(arc.startLat, arc.startLon);
            const t = (now - arc.startTime) / arc.duration;
            
            const midX = (startXY.x + targetXY.x) / 2;
            const midY = (startXY.y + targetXY.y) / 2 - 40;
            
            ctx.strokeStyle = `rgba(255, 0, 60, ${0.45 * (1 - t)})`;
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.moveTo(startXY.x, startXY.y);
            ctx.quadraticCurveTo(midX, midY, targetXY.x, targetXY.y);
            ctx.stroke();
            
            const partX = (1-t)*(1-t)*startXY.x + 2*(1-t)*t*midX + t*t*targetXY.x;
            const partY = (1-t)*(1-t)*startXY.y + 2*(1-t)*t*midY + t*t*targetXY.y;
            
            ctx.fillStyle = '#ff003c';
            ctx.beginPath();
            ctx.arc(partX, partY, 3, 0, Math.PI * 2);
            ctx.fill();
        });
        
        requestAnimationFrame(animate);
    }
    
    requestAnimationFrame(animate);
}

function triggerAttackArc(ipAddress) {
    if (!ipAddress) return;
    
    let lat = 0;
    let lon = 0;
    let country = "Unknown";
    
    if (ipAddress.startsWith("127.") || ipAddress.startsWith("192.168.") || ipAddress.startsWith("10.") || ipAddress.startsWith("172.")) {
        lat = 39.5;
        lon = -121.5;
        country = "Local Intranet";
    } else {
        let hash = 0;
        for (let i = 0; i < ipAddress.length; i++) {
            hash = ipAddress.charCodeAt(i) + ((hash << 5) - hash);
        }
        
        const locations = [
            {lat: 51.5, lon: -0.1, country: "United Kingdom"},
            {lat: 35.6, lon: 139.6, country: "Japan"},
            {lat: -33.8, lon: 151.2, country: "Australia"},
            {lat: 48.8, lon: 2.3, country: "France"},
            {lat: -22.9, lon: -43.1, country: "Brazil"},
            {lat: 55.7, lon: 37.6, country: "Russia"},
            {lat: 28.6, lon: 77.2, country: "India"},
            {lat: 39.9, lon: 116.4, country: "China"},
            {lat: -34.6, lon: -58.3, country: "Argentina"},
            {lat: 1.3, lon: 103.8, country: "Singapore"}
        ];
        
        const loc = locations[Math.abs(hash) % locations.length];
        lat = loc.lat + ((hash % 8) / 4.0);
        lon = loc.lon + (((hash >> 3) % 8) / 4.0);
        country = loc.country;
    }
    
    activeMapArcs.push({
        startLat: lat,
        startLon: lon,
        startTime: Date.now(),
        duration: 1600
    });
    
    const overlay = document.getElementById('map-target-status');
    if (overlay) {
        overlay.innerHTML = `<span class="text-cyber-accent font-bold">THREAT INGESTION:</span> IP ${ipAddress} mapped to origin ${country}`;
        setTimeout(() => {
            overlay.innerHTML = `<span class="text-cyber-success font-bold">MONITOR ACTIVE:</span> Waiting for logs...`;
        }, 4000);
    }
}

// 5. Forensic Relationship Graph Engine
let graphNodes = [];
let graphLinks = [];
let selectedNode = null;
let isDraggingNode = false;

function initInvestigationGraph() {
    const canvas = document.getElementById('investigation-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    function resizeGraphCanvas() {
        if (!canvas) return;
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = canvas.parentElement.clientHeight;
    }
    resizeGraphCanvas();
    
    graphNodes = [];
    graphLinks = [];
    
    const searchIp = document.getElementById('investigate-ip').value.trim();
    if (!searchIp) return;
    
    fetchForensicData(searchIp);
    
    function drawGraph() {
        if (!canvas) return;
        ctx.fillStyle = '#060a13';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Repel nodes physics
        for (let i = 0; i < graphNodes.length; i++) {
            for (let j = i + 1; j < graphNodes.length; j++) {
                const n1 = graphNodes[i];
                const n2 = graphNodes[j];
                const dx = n2.x - n1.x;
                const dy = n2.y - n1.y;
                const dist = Math.sqrt(dx * dx + dy * dy) || 1;
                if (dist < 100) {
                    const force = (100 - dist) * 0.04;
                    const fx = (dx / dist) * force;
                    const fy = (dy / dist) * force;
                    if (!n1.fixed) { n1.x -= fx; n1.y -= fy; }
                    if (!n2.fixed) { n2.x += fx; n2.y += fy; }
                }
            }
        }
        
        // Pull along links physics
        graphLinks.forEach(link => {
            const sourceNode = graphNodes.find(n => n.id === link.source);
            const targetNode = graphNodes.find(n => n.id === link.target);
            if (sourceNode && targetNode) {
                const dx = targetNode.x - sourceNode.x;
                const dy = targetNode.y - sourceNode.y;
                const dist = Math.sqrt(dx * dx + dy * dy) || 1;
                const force = (dist - 90) * 0.015;
                const fx = (dx / dist) * force;
                const fy = (dy / dist) * force;
                if (!sourceNode.fixed) { sourceNode.x += fx; sourceNode.y += fy; }
                if (!targetNode.fixed) { targetNode.x -= fx; targetNode.y -= fy; }
            }
        });
        
        // Maintain inside bounds
        graphNodes.forEach(node => {
            if (node.x < 20) node.x = 20;
            if (node.x > canvas.width - 20) node.x = canvas.width - 20;
            if (node.y < 20) node.y = 20;
            if (node.y > canvas.height - 20) node.y = canvas.height - 20;
        });

        // Draw links
        ctx.strokeStyle = 'rgba(0, 242, 254, 0.15)';
        ctx.lineWidth = 1;
        ctx.setLineDash([4, 4]);
        graphLinks.forEach(link => {
            const sourceNode = graphNodes.find(n => n.id === link.source);
            const targetNode = graphNodes.find(n => n.id === link.target);
            if (sourceNode && targetNode) {
                ctx.beginPath();
                ctx.moveTo(sourceNode.x, sourceNode.y);
                ctx.lineTo(targetNode.x, targetNode.y);
                ctx.stroke();
            }
        });
        ctx.setLineDash([]);
        
        // Draw nodes
        graphNodes.forEach(node => {
            let color = '#718096';
            let glow = false;
            let radius = 9;
            
            if (node.type === 'attacker') {
                color = '#ff003c';
                glow = true;
                radius = 15;
            } else if (node.type === 'service') {
                color = '#00f2fe';
                radius = 11;
            } else if (node.type === 'alert') {
                color = '#ffb300';
                glow = true;
                radius = 13;
            }
            
            if (glow) {
                ctx.shadowColor = color;
                ctx.shadowBlur = 10;
            }
            
            ctx.fillStyle = color;
            ctx.beginPath();
            ctx.arc(node.x, node.y, radius, 0, Math.PI * 2);
            ctx.fill();
            ctx.shadowBlur = 0;
            
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.35)';
            ctx.lineWidth = 1.2;
            ctx.stroke();
            
            ctx.fillStyle = '#e2e8f0';
            ctx.font = '9px monospace';
            ctx.textAlign = 'center';
            ctx.fillText(node.label, node.x, node.y - radius - 4);
        });
        
        requestAnimationFrame(drawGraph);
    }
    
    canvas.onmousedown = function(e) {
        const rect = canvas.getBoundingClientRect();
        const mx = e.clientX - rect.left;
        const my = e.clientY - rect.top;
        
        selectedNode = graphNodes.find(node => {
            const dx = node.x - mx;
            const dy = node.y - my;
            return Math.sqrt(dx * dx + dy * dy) < 20;
        });
        
        if (selectedNode) {
            isDraggingNode = true;
            selectedNode.fixed = true;
        }
    };
    
    canvas.onmousemove = function(e) {
        if (isDraggingNode && selectedNode) {
            const rect = canvas.getBoundingClientRect();
            selectedNode.x = e.clientX - rect.left;
            selectedNode.y = e.clientY - rect.top;
        }
    };
    
    canvas.onmouseup = function(e) {
        if (selectedNode) {
            selectedNode.fixed = false;
        }
        isDraggingNode = false;
        selectedNode = null;
    };
    
    requestAnimationFrame(drawGraph);
}

async function fetchForensicData(ip) {
    const statusText = document.getElementById('graph-status');
    statusText.innerText = "Querying host relationships...";
    try {
        const response = await fetch(`/api/v1/investigate/${ip}`);
        const data = await response.json();
        if (response.ok) {
            const canvas = document.getElementById('investigation-canvas');
            const cx = canvas.width / 2;
            const cy = canvas.height / 2;
            
            graphNodes = data.nodes.map(n => ({
                ...n,
                x: cx + (Math.random() - 0.5) * 150,
                y: cy + (Math.random() - 0.5) * 150,
                fixed: false
            }));
            graphLinks = data.links;
            statusText.innerText = `Discovered ${graphNodes.length} nodes and ${graphLinks.length} edges.`;
        } else {
            statusText.innerText = `Retrieval failed: ${data.detail}`;
        }
    } catch (err) {
        statusText.innerText = `Network fault: ${err.message}`;
    }
}

// 6. Threat Intelligence & Blocks Registry loaders
async function fetchIndicatorsCatalog() {
    const tbody = document.getElementById('db-indicators-tbody');
    if (!tbody) return;

    try {
        const response = await fetch('/api/v1/indicators/');
        const data = await response.json();
        if (response.ok) {
            if (data.length === 0) {
                tbody.innerHTML = `<tr><td colspan="5" class="text-center font-mono text-[10px] text-cyber-muted py-8">Threat Intel Catalog empty. Sync to populate.</td></tr>`;
            } else {
                tbody.innerHTML = data.map(item => `
                    <tr>
                        <td class="font-mono text-cyber-accent text-[10px]">${item.indicator_value}</td>
                        <td class="text-[10px] font-mono">${item.indicator_type}</td>
                        <td class="text-[10px]">${item.threat_actor || 'Unknown'}</td>
                        <td class="text-[10px] font-mono text-center text-cyber-danger font-bold">${item.risk_score}</td>
                        <td class="text-[10px] text-cyber-muted">${item.description}</td>
                    </tr>
                `).join('');
            }
        }
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center font-mono text-[10px] text-cyber-danger py-8">Failed to fetch threat indicators.</td></tr>`;
    }
}

async function fetchBlockedRegistry() {
    const tbody = document.getElementById('db-blocked-tbody');
    if (!tbody) return;

    try {
        const response = await fetch('/api/v1/indicators/blocked');
        const data = await response.json();
        if (response.ok) {
            if (data.length === 0) {
                tbody.innerHTML = `<tr><td colspan="4" class="text-center font-mono text-[10px] text-cyber-muted py-8">No active blocked policies in firewall registry.</td></tr>`;
            } else {
                tbody.innerHTML = data.map(item => `
                    <tr>
                        <td class="text-[9px] font-mono text-cyber-muted">${new Date(item.blocked_at).toLocaleTimeString()}</td>
                        <td class="font-mono text-cyber-danger text-[10px]">${item.ip_address}</td>
                        <td class="text-[10px]">${item.rule_name || 'Generic Rule Block'}</td>
                        <td class="text-center"><span class="status-indicator success text-[8px] py-0.5 px-1.5">${item.status}</span></td>
                    </tr>
                `).join('');
            }
        }
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="4" class="text-center font-mono text-[10px] text-cyber-danger py-8">Failed to load blocks registry.</td></tr>`;
    }
}

// 7. Core Incident Playbook Generation override
async function generatePlaybookFor(alertId) {
    appendChatMessage('user', `Generate incident response playbook for Alert ID #${alertId}`);
    
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
            const messageId = appendChatMessage('assistant', data.reply);
            
            const msgEl = document.getElementById(messageId);
            if (msgEl) {
                const textContainer = msgEl.querySelector('.text-cyber-light');
                if (textContainer) {
                    textContainer.innerHTML += `
                        <div class="mt-4 pt-3 border-t border-cyber-border/20 flex flex-col gap-2">
                            <div class="text-[10px] text-cyber-accent font-bold uppercase tracking-wider font-mono">SOAR ORCHESTRATION ACTIONS:</div>
                            <button id="remediate-btn-${alertId}" onclick="executePlaybookRemediation(${alertId}, '${messageId}')" class="cyber-btn primary py-1.5 px-3 text-[10px] w-fit font-bold tracking-wider">
                                EXECUTE REMEDIATION PLAYBOOK
                            </button>
                        </div>
                    `;
                }
            }
        } else {
            appendChatMessage('assistant', `<span class="text-cyber-danger">[Error] Failed to generate playbook: ${data.detail}</span>`);
        }
    } catch (err) {
        removeChatMessage(loadingId);
        appendChatMessage('assistant', `<span class="text-cyber-danger">[Error] socket error: ${err.message}</span>`);
    }
}

// 8. SOAR Active Containment command orchestration
window.executePlaybookRemediation = async function(alertId, messageId) {
    const btn = document.getElementById(`remediate-btn-${alertId}`);
    if (btn) {
        btn.disabled = true;
        btn.innerText = "EXECUTING PLAYBOOK REMEDIATION...";
        btn.classList.add('animate-pulse');
    }

    try {
        const response = await fetch(`/api/v1/ai/playbook/${alertId}/remediate`, {
            method: 'POST'
        });
        const data = await response.json();

        if (response.ok) {
            const msgEl = document.getElementById(messageId);
            if (msgEl) {
                const textContainer = msgEl.querySelector('.text-cyber-light');
                if (textContainer) {
                    btn.remove();
                    
                    let logHtml = `<div class="mt-3 p-3 bg-cyber-dark/80 border border-cyber-success/35 rounded font-mono text-[9px] text-cyber-success space-y-1.5 animate-fade-in">`;
                    data.execution_log.forEach(line => {
                        logHtml += `<div><span class="text-cyber-muted">&gt;</span> ${line}</div>`;
                    });
                    logHtml += `</div>`;
                    textContainer.innerHTML += logHtml;
                }
            }
            
            // Mark alert status resolved locally
            await fetch(`/api/v1/alerts/${alertId}/status?status=RESOLVED`, { method: 'PATCH' });
            
            fetchBlockedRegistry();
            fetchDBAlerts();
            loadCopilotAlerts();
        } else {
            alert(`SOAR Execution error: ${data.detail}`);
            if (btn) {
                btn.disabled = false;
                btn.innerText = "EXECUTE REMEDIATION PLAYBOOK";
                btn.classList.remove('animate-pulse');
            }
        }
    } catch (err) {
        alert(`SOAR Connection error: ${err.message}`);
        if (btn) {
            btn.disabled = false;
            btn.innerText = "EXECUTE REMEDIATION PLAYBOOK";
            btn.classList.remove('animate-pulse');
        }
    }
};

// Global exports & initialization boots
window.sendCopilotSuggested = function(text) {
    const input = document.getElementById('chat-user-message');
    if (input) {
        input.value = text;
        const form = document.getElementById('chat-input-form');
        if (form) form.dispatchEvent(new Event('submit'));
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
    
    container.scrollTop = container.scrollHeight;
    return messageId;
}

function removeChatMessage(messageId) {
    const el = document.getElementById(messageId);
    if (el) el.remove();
}

function formatMarkdown(text) {
    if (!text) return "";
    
    let html = text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");

    html = html.replace(/```(?:[a-zA-Z0-9]+)?
([\s\S]*?)```/g, (match, p1) => {
        return `<pre class="bg-cyber-dark border border-cyber-border/40 p-3 rounded font-mono text-[11px] text-cyber-accent my-2 overflow-x-auto select-text">${p1.trim()}</pre>`;
    });

    html = html.replace(/`([^`]+)`/g, '<code class="bg-cyber-dark/60 text-cyber-accent px-1.5 py-0.5 rounded font-mono text-[10px]">$1</code>');
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong class="text-cyber-light font-bold">$1</strong>');
    html = html.replace(/^### (.*$)/gim, '<h4 class="text-xs font-bold text-cyber-light mt-3 border-b border-cyber-border/20 pb-1 mb-1">$1</h4>');
    html = html.replace(/^## (.*$)/gim, '<h3 class="text-sm font-bold text-cyber-light mt-4 border-b border-cyber-border/30 pb-1 mb-1">$1</h3>');
    html = html.replace(/^# (.*$)/gim, '<h2 class="text-md font-bold text-cyber-accent mt-5 border-b border-cyber-border/40 pb-1 mb-1">$1</h2>');
    html = html.replace(/^\s*-\s+(.*$)/gim, '<li class="list-disc list-inside text-cyber-muted ml-2 py-0.5">$1</li>');

    const parts = html.split(/(<pre[\s\S]*?<\/pre>)/g);
    for (let i = 0; i < parts.length; i++) {
        if (!parts[i].startsWith('<pre')) {
            parts[i] = parts[i].replace(/
/g, '<br>');
        }
    }
    return parts.join('');
}

// Dom Bootload Initializer
document.addEventListener('DOMContentLoaded', () => {
    initInteractivity();
    initAttackMap();
    
    // Auto load assets on initial view
    setTimeout(() => {
        fetchDBLogs();
        fetchDBAlerts();
    }, 100);
});
