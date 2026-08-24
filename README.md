# AI-Powered Packaged Product Compliance Verification System

An automated, evidence-grounded verification system for auditing packaged consumer commodities against the **Legal Metrology (Packaged Commodities) Rules, 2011**.

---

## 🏗️ Architecture & Pipeline

```
Uploaded Package Image
         ↓
1. Image Validation & Preprocessing (Pillow, OpenCV, CLAHE/Binarization)
         ↓
2. Optical Character Recognition (PaddleOCR Engine)
         ↓
3. NLP Declaration Extraction & Normalization (Regex + Rule Parsers)
         ↓
4. Relational Persistence (SQLAlchemy 2.x, PostgreSQL/SQLite)
         ↓
5. Deterministic Compliance RuleEngine (Authoritative Legal Metrology Decision)
         ↓
6. Evidence-Grounded AI Explanation (Gemini / OpenAI / Deterministic Baseline)
         ↓
7. Consolidated Response & React Frontend Dashboard (Vite, React, Tailwind)
```

---

## 🚀 Quick Start

### 1. Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env

# Run FastAPI backend server
python -m uvicorn backend.app:app --reload --port 8000
```
- Interactive API Docs (Swagger): `http://127.0.0.1:8000/docs`
- Health Check: `http://127.0.0.1:8000/api/health`

### 2. Frontend Setup

```bash
cd frontend

# Install Node dependencies
npm install

# Start Vite Development Server
npm run dev

# Production Build
npm run build
```
- Frontend UI: `http://localhost:5173`

---

## 🐳 Docker Deployment

To launch the full production stack (PostgreSQL, FastAPI Backend, and Nginx-served Frontend):

```bash
docker-compose up --build -d
```

- **Frontend App**: `http://localhost`
- **Backend API**: `http://localhost:8000`
- **PostgreSQL**: `localhost:5432`

---

## 🔒 Security & Production Hardening

- **CORS Protection**: Configurable allowed origins via `CORS_ORIGINS` environment variable.
- **Upload Constraints**: Enforced 20 MB max file size, allowed MIME types (`image/jpeg`, `image/png`, `image/webp`, `image/bmp`, `image/tiff`), and filename path-traversal sanitization.
- **Error Privacy**: Production 500 errors return sanitized error payloads without internal exception leakages or file paths.
- **Deterministic Compliance**: AI models provide evidence explanations and remediation suggestions only; statutory compliance scores and pass/fail decisions are 100% evaluated by the deterministic rule engine.
- **Resilient AI Fallback**: Verification succeeds with deterministic regulatory explanations even when external LLM APIs are offline or unconfigured.

---

## 🧪 Automated Testing

Run the full backend unit, integration, and security regression suite:

```bash
python -m pytest -v
```
