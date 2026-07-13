# Qyverion // AI-Powered Security Operations Center (SOC)

Qyverion is a production-grade, modular, and scalable Security Operations Center (SOC) platform designed for centralized log ingestion, threat detection, security incident investigation, threat intelligence enrichment, and AI-assisted security analysis.

This repository contains the core codebase for Qyverion, structured using clean architecture principles to ensure decoupling of business logic, database implementations, and presentation layers.

---

## 🛠️ Technology Stack

### Backend Console
* **Runtime:** Python 3.13+
* **Web Server Framework:** FastAPI (Asynchronous API endpoints)
* **ASGI Server:** Uvicorn (High-performance process worker)
* **Database Object-Relational Mapper (ORM):** SQLAlchemy 2.x (Modern declarative mappings)
* **Migration Engine:** Alembic (Incremental schema management)
* **Configuration & Validation:** Pydantic / Pydantic Settings
* **Database Driver:** Psycopg2 (PostgreSQL adapter)

### Frontend Console
* **Presentation Layer:** Vanilla HTML5, Vanilla CSS3 (Custom-designed dark theme system), and Modern ES6+ JavaScript.
* **Serving Mechanism:** Mounted directly via FastAPI static files at root path `/` to eliminate JavaScript toolchain overhead during early development phases.
* **Icons & Typography:** Google Fonts (Outfit & JetBrains Mono), Lucide Icons.

---

## 📂 Project Architecture & Structure

The repository follows clean architecture design guidelines:

```text
Qyverion/
│
├── .github/                # GitHub Action workflows & issue/PR templates
├── datasets/               # Sample log files and raw ingestion datasets
├── docs/                   # System design documents and developer guides
├── scripts/                # Database seeds and deployment automation scripts
│
├── frontend/               # Static frontend client interface
│   ├── css/
│   │   └── style.css       # Vanilla CSS design tokens & layouts
│   ├── js/
│   │   └── app.js          # Client-side routing, canvas node logic, and bootlogs
│   └── index.html          # Core framework console landing page
│
├── backend/                # FastAPI application engine
│   ├── alembic/            # Database schema version migrations
│   │   ├── versions/       # Individual incremental migration scripts
│   │   └── env.py          # Dynamic configuration loader for migrations
│   │
│   ├── app/                # Main application package
│   │   ├── api/            # API routing and HTTP controller request boundaries
│   │   ├── config/         # App-wide settings entrypoint
│   │   ├── core/           # Central settings, logging setups, security variables
│   │   │   ├── config.py   # Pydantic Settings loader parses .env
│   │   │   └── logging_config.py # Structured logger setup
│   │   ├── db/             # SQLAlchemy connection session configurations
│   │   │   ├── base.py     # Base Declarative class (auto-tablenames)
│   │   │   └── session.py  # Local connection sessions & dependency injectors
│   │   ├── middleware/     # Custom HTTP request/response interceptors (CORS, timers)
│   │   ├── models/         # Database persistence definitions (SQLAlchemy models)
│   │   ├── schemas/        # Request validation and serialization (Pydantic schemas)
│   │   ├── repositories/   # Database access layer pattern (Separation of Concerns)
│   │   ├── services/       # Core SOC business domain logic (Threat detection engines)
│   │   ├── utils/          # Cross-cutting utility modules (Hashing, encryption)
│   │   └── main.py         # Entrypoint bootstrapper mounts routes & frontend
│   │
│   └── alembic.ini         # Alembic configuration metadata template
│
├── .env.example            # Environment variables configuration template
├── .gitignore              # Multi-language build and config ignore rules
├── requirements.txt        # Frozen dependency definitions
└── README.md               # Main developer reference manual
```

---

## ⚙️ Installation & Local Setup

### Prerequisites
* **Python 3.13+** installed locally.
* **PostgreSQL** instance running locally on port `5432`.

### Step 1: Clone & Configure Workspace
Create your local environment file by cloning the template:
```bash
cp .env.example .env
```
Open `.env` in your editor and adjust your local PostgreSQL settings:
```ini
POSTGRES_USER="postgres"
POSTGRES_PASSWORD="your_secure_postgresql_password"
POSTGRES_DB="qyverion"
DATABASE_URL="postgresql://postgres:your_secure_postgresql_password@localhost:5432/qyverion"
```

### Step 2: Establish Virtual Environment (venv)
In the root directory, create a local Python virtual environment to isolate dependencies:
```bash
# Create the local venv
python -m venv .venv

# Activate the venv (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Activate the venv (Linux / macOS)
source .venv/bin/activate
```

### Step 3: Install Core Dependencies
With the virtual environment active, run the installation:
```bash
pip install -r requirements.txt
```

---

## 🚀 Running the Platform

### Running the Backend & Frontend (Unified Command)
FastAPI serves the frontend client directly. To boot the unified web server, ensure your virtual environment is active, then execute:

```bash
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

* **Interactive Frontend Console:** Open `http://127.0.0.1:8000/` in your browser.
* **Auto-Generated Swagger API Documentation:** Open `http://127.0.0.1:8000/api/v1/docs` in your browser.
* **Live System Health Check API:** Open `http://127.0.0.1:8000/api/v1/health`.

---

## 🛠️ Verification & Diagnostic Checklist

Before pushing changes, run the following verification checks:

1. **Syntax Integrity Check:**
   Ensure all python packages compilation matches:
   ```bash
   python -m py_compile backend/app/main.py
   ```
2. **Settings Loader Integrity:**
   Verify Pydantic parses configuration values accurately:
   ```bash
   python -c "from backend.app.core.config import settings; print('Settings loaded successfully for:', settings.PROJECT_NAME)"
   ```
3. **Database Engine Integration:**
   Check if the database engine establishes standard connection parameters:
   ```bash
   python -c "from backend.app.db.session import engine; conn=engine.connect(); print('DB connection state active:', not conn.closed); conn.close()"
   ```

---

## 🔮 Future Roadmap

* **Day 2 (Next Step):**
  * Implement base database models (e.g., `logs`, `users`, `threats`).
  * Implement Pydantic request/response validation schemas.
  * Formulate the mock backend API router endpoints for log uploads and alert listings.
  * Write the first set of unit and integration test suites using `pytest`.
* **Day 3-5:**
  * Threat Ingestion Pipeline (Parsers for syslog, JSON, Windows Events).
  * Detection Engine execution using sigma rules and static thresholds.
  * Integration with LLM providers for AI-driven security analyst advice and copilot integrations.
  * Interactive incident timeline visualization on the frontend.

---

## 📝 License

This project is licensed under a proprietary enterprise license. Unauthorized copying or redistribution is strictly prohibited.
