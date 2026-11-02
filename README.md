# ARI — Multilingual RAG Knowledge Assistant

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blueviolet?style=flat-square" />
  <img src="https://img.shields.io/badge/FastAPI-0.115-pink?style=flat-square" />
  <img src="https://img.shields.io/badge/React-18-blue?style=flat-square" />
  <img src="https://img.shields.io/badge/xAI_Grok-4.7-black?style=flat-square" />
  <img src="https://img.shields.io/badge/ChromaDB-Persistent-green?style=flat-square" />
</p>

> **Knowledge, in every language.** — ARI is a production-quality multilingual Retrieval-Augmented Generation (RAG) assistant powered by xAI Grok, `intfloat/multilingual-e5-base` embeddings, and persistent ChromaDB vector storage.

---

## ✨ Features

- **Multilingual RAG** — Upload documents in any language, ask questions in Hindi, Arabic, Spanish, French, Marathi, Bengali, Tamil, Telugu, German, or English
- **xAI Grok Integration** — Official `/v1/responses` endpoint with exponential backoff and rate-limit retry logic
- **Clickable Source Citations** — Every answer links to exact document chunk, page number, and similarity score
- **Persistent Vector Storage** — ChromaDB stores embeddings between restarts
- **Multiple Knowledge Bases** — Create isolated KB collections per topic or project
- **Chat History** — SQLite-backed multi-turn conversation memory
- **Eternal Sunshine UI** — Ariana Grande–inspired glassmorphism design (blush pink, lavender, mauve)

---

## 🗂 Project Structure

```
ARI/
├── backend/
│   ├── app/
│   │   ├── api/endpoints/   # chat, documents, health, knowledge_bases, settings
│   │   ├── core/            # config, logging, security
│   │   ├── database/        # SQLite session & repository
│   │   ├── models/          # Pydantic schemas & SQLAlchemy models
│   │   ├── rag/             # document_loader, embeddings, pipeline, text_splitter, vector_store
│   │   ├── services/        # grok_service, language_service
│   │   └── main.py
│   ├── .env                 # ← Your secrets go here (never committed)
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # Root router & page switcher
│   │   ├── main.tsx         # React entry point
│   │   ├── components/      # Navbar, CitationCard
│   │   ├── pages/           # LandingPage, ChatDashboard, KnowledgeBasePage, SettingsPage
│   │   ├── services/        # api.ts (typed fetch client)
│   │   ├── styles/          # index.css (Tailwind + glassmorphism)
│   │   └── types/           # TypeScript interfaces
│   ├── vite.config.ts       # Vite proxy → backend:8000
│   └── tailwind.config.js
└── storage/
    ├── chroma/              # Persistent ChromaDB vector data
    ├── database/            # ari.db (SQLite)
    └── documents/           # Uploaded files
```

---

## 🚀 Quick Start

### Prerequisites

- **Python** 3.11+ with `uv` (`pip install uv`)
- **Node.js** v18+ with `npm`
- An **xAI API key** from [x.ai](https://x.ai)

---

### 1. Backend Setup

```powershell
# Navigate to backend
cd ARI\backend

# Create virtual environment and install dependencies
uv venv --python 3.11
uv pip install -r requirements.txt

# Copy example env and add your key
Copy-Item .env.example .env
# Edit .env and set XAI_API_KEY=xai-...
notepad .env
```

**`.env` contents:**
```env
XAI_API_KEY=xai-YOUR_KEY_HERE
GROK_MODEL=grok-4.7
XAI_BASE_URL=https://api.x.ai/v1
EMBEDDING_MODEL=intfloat/multilingual-e5-base
SIMILARITY_THRESHOLD=0.35
TOP_K_RESULTS=4
CHUNK_SIZE=800
CHUNK_OVERLAP=120
CHROMA_PATH=../storage/chroma
DATABASE_PATH=../storage/database/ari.db
UPLOAD_DIR=../storage/documents
PORT=8000
HOST=0.0.0.0
FRONTEND_ORIGIN=http://localhost:5173
```

**Start the backend:**
```powershell
cd ARI\backend
.\.venv\Scripts\uvicorn.exe app.main:app --reload --host 127.0.0.1 --port 8000
```

On first start, the `multilingual-e5-base` model (~560MB) is downloaded from HuggingFace automatically.

---

### 2. Frontend Setup

```powershell
cd ARI\frontend
npm install   # (already done if node_modules exists)
npm run dev
```

Frontend starts at **http://localhost:5173** and proxies `/api/*` → `http://127.0.0.1:8000`.

---

### 3. Verify Everything Works

Open **http://localhost:5173** in your browser. You should see:

1. **Navbar** — Grok badge shows "Key Missing" (amber) until API key is set, then "Configured" (green)
2. **Landing Page** — Beautiful ARI hero section
3. **Settings → Run Live Grok Diagnostic** — tests live xAI connection
4. **Knowledge Base** — upload a PDF and watch it chunk + index
5. **Chat** — ask questions in any language!

---

## 🔧 API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/` | Root info |
| GET | `/api/health` | Backend + services health |
| GET | `/api/health/grok?test_live=true` | Grok connection test |
| GET | `/api/health/embeddings` | Embedding engine status |
| GET | `/api/health/vector-db` | ChromaDB status |
| GET | `/api/settings` | All RAG/system settings |
| GET | `/api/knowledge-bases` | List all knowledge bases |
| POST | `/api/knowledge-bases` | Create knowledge base |
| DELETE | `/api/knowledge-bases/{id}` | Delete KB |
| POST | `/api/documents/upload` | Upload + index document |
| GET | `/api/documents?knowledge_base_id=...` | List documents |
| DELETE | `/api/documents/{id}` | Delete document + vectors |
| POST | `/api/documents/{id}/reindex` | Re-embed document |
| POST | `/api/chat` | Send RAG chat message |
| GET | `/api/chat/history` | List conversations |
| GET | `/api/chat/{id}` | Get conversation + messages |
| PATCH | `/api/chat/{id}` | Rename conversation |
| DELETE | `/api/chat/{id}` | Delete conversation |

Interactive docs: **http://localhost:8000/docs**

---

## 🌍 Supported Languages

| Language | Code | Script | Direction |
|---|---|---|---|
| English | en | Latin | LTR |
| Hindi (हिन्दी) | hi | Devanagari | LTR |
| Marathi (मराठी) | mr | Devanagari | LTR |
| Bengali (বাংলা) | bn | Bengali | LTR |
| Tamil (தமிழ்) | ta | Tamil | LTR |
| Telugu (తెలుగు) | te | Telugu | LTR |
| Spanish (Español) | es | Latin | LTR |
| French (Français) | fr | Latin | LTR |
| German (Deutsch) | de | Latin | LTR |
| Arabic (العربية) | ar | Arabic | RTL |

---

## 🛡 Security Notes

- `XAI_API_KEY` lives **only** in `backend/.env` — never sent to frontend, never logged
- Upload validation: allowed extensions (PDF, DOCX, TXT, MD), 25MB size limit
- Global exception handler sanitizes error messages (no stack traces in responses)
- CORS locked to `localhost:5173` and `localhost:3000` by default

---

## 🐛 Troubleshooting

| Problem | Fix |
|---|---|
| Grok badge shows "Key Missing" | Add `XAI_API_KEY` to `backend/.env` and restart backend |
| Embedding model download stuck | First startup downloads ~560MB; wait or check network |
| `CORS` errors in browser | Ensure backend is on port 8000 and frontend on 5173 |
| ChromaDB path errors | Storage directories auto-created; check write permissions |
| PDF parse fails | Update PyMuPDF: `uv pip install --upgrade PyMuPDF` |

---

## 📐 Architecture

```
User Query (any language)
       ↓
Language Detection (langdetect)
       ↓
Embedding: "query: {text}" → 768-dim vector (multilingual-e5-base)
       ↓
ChromaDB cosine similarity search (threshold: 0.35, top-k: 4)
       ↓
If chunks found → Build grounded prompt with <retrieved_context>
       ↓
xAI Grok /v1/responses → Grounded answer in user's language
       ↓
Citations extracted → Persisted to SQLite → Returned to UI
```
