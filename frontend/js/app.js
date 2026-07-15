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

// 3. Tab Navigation & Live API Interactivity
function initInteractivity() {
    const navOverview = document.getElementById('nav-overview');
    const navIngestion = document.getElementById('nav-ingestion');
    const tabOverview = document.getElementById('tab-overview');
    const tabIngestion = document.getElementById('tab-ingestion');

    if (!navOverview || !navIngestion) return;

    // Tab switching controls
    navOverview.addEventListener('click', (e) => {
        e.preventDefault();
        navOverview.classList.add('active');
        navIngestion.classList.remove('active');
        tabOverview.classList.remove('hidden');
        tabIngestion.classList.add('hidden');
    });

    navIngestion.addEventListener('click', (e) => {
        e.preventDefault();
        navIngestion.classList.add('active');
        navOverview.classList.remove('active');
        tabIngestion.classList.remove('hidden');
        tabOverview.classList.add('hidden');
        
        // Load database records dynamically on tab transition
        fetchDBLogs();
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

    // Refresh button listener
    const refreshBtn = document.getElementById('refresh-logs-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            fetchDBLogs();
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
