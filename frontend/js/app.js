// Qyverion Day 1 - Frontend Interaction & Canvas Visualization

document.addEventListener('DOMContentLoaded', () => {
    initCanvas();
    initBootLogs();
});

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

// 2. Mock System Bootlog Streaming
const MOCK_LOGS = [
    { type: 'info', tag: 'SYS', msg: 'Initializing Qyverion Platform Foundation (Day 1)...' },
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
        
        // Random slight delays between 300ms and 800ms for natural feel
        setTimeout(addLogLine, Math.random() * 500 + 200);
    }
    
    // Start streaming logs
    addLogLine();
    
    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            container.innerHTML = '';
            logIndex = 0;
            addLogLine();
        });
    }
}
