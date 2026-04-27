<div align="center">

<!-- Animated Header -->
<img src="https://capsule-render.vercel.app/api?type=waving&color=0:1e3a5f,50:2563eb,100:7c3aed&height=220&section=header&text=IVERI%20LLM&fontSize=80&fontColor=ffffff&animation=fadeIn&fontAlignY=35&desc=Intelligent%20AI%20Learning%20%26%20Student%20Monitoring%20System&descAlignY=55&descSize=18&descColor=d1d5db" width="100%" />

<!-- Badges -->
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)
[![FAISS](https://img.shields.io/badge/FAISS-Vector%20Search-4285F4?style=for-the-badge&logo=meta&logoColor=white)](https://github.com/facebookresearch/faiss)
[![Sarvam](https://img.shields.io/badge/LLM-Sarvam--M-FF6B35?style=for-the-badge&logo=openai&logoColor=white)](https://sarvam.ai)

<br/>

<!-- Stats -->
![GitHub repo size](https://img.shields.io/github/repo-size/Nishant-aiml/iveri-llm-advanced-rag-learning-system?style=flat-square&color=blue)
![GitHub last commit](https://img.shields.io/github/last-commit/Nishant-aiml/iveri-llm-advanced-rag-learning-system?style=flat-square&color=green)
![GitHub stars](https://img.shields.io/github/stars/Nishant-aiml/iveri-llm-advanced-rag-learning-system?style=flat-square&color=yellow)
![GitHub forks](https://img.shields.io/github/forks/Nishant-aiml/iveri-llm-advanced-rag-learning-system?style=flat-square&color=orange)
![GitHub issues](https://img.shields.io/github/issues/Nishant-aiml/iveri-llm-advanced-rag-learning-system?style=flat-square&color=red)

<br/>

> **A production-grade Retrieval-Augmented Generation (RAG) pipeline** combining hybrid information retrieval, multi-stage reranking, grounded LLM generation, and evaluation-driven optimization — delivering a personalized AI learning and student monitoring platform.

<br/>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%" />

</div>

## ⚡ Quick Overview

```
📄 Upload a Document  →  🧠 AI Processes & Indexes  →  🎯 Ask, Search, Quiz, Learn
```

## ⚡ What this is (in 20 seconds)

**IVERI LLM** is an AI learning platform that turns PDFs into:
- a **Google-like search engine** (Keyword / Hybrid / AI / Auto)
- an **NPTEL/Coursera-like Course View** (Subject → Unit → Topic → Subtopic → Content)
- **grounded Q&A** (answer + sources + confidence, safe fallback)
- **practice loop** (quizzes, mock tests, flashcards)
- **personalization** (weakness detection + study recommendations)

## 🧩 Problem → Solution (simple)

### Problem
- PDFs are hard to study from: no structure, slow navigation, and "chat with PDF" hallucinates.
- Search is either keyword-only (misses meaning) or vector-only (misses exact terms).
- Students need feedback loops: practice + weak-topic tracking + targeted revision.

### Solution
IVERI LLM runs an end-to-end pipeline:
- **Ingestion**: parse → clean → chunk → index (BM25 + FAISS) → build **unified hierarchy**
- **Retrieval**: Hybrid RRF fusion + optional rerank + MMR diversity
- **Trust layer**: confidence + citations; low confidence returns "not in document"
- **Learning UX**: Course View + Search + Quiz + Flashcards + Weakness dashboard

<table>
<tr>
<td width="50%">

### 🎓 For Students
- 🤖 Ask AI — Get grounded answers from your documents
- 🔍 Google-like Search — Keyword, Hybrid, or AI mode
- 📝 Auto-generated Quizzes & Mock Tests
- 📊 Weakness Detection & Personalized Recommendations
- 🃏 Flashcards for quick revision
- 🏆 Gamification — XP, Levels, Leaderboard
- 📚 Course View — Structured hierarchical reading
- 💡 AI Mentor — Context-aware chat assistant

</td>
<td width="50%">

### 👨‍🏫 For Educators
- 📚 Subject-based Content Library
- 🔄 LLM Auto-Classification of documents
- 📈 Student performance monitoring
- 🎯 50+ question evaluation engine
- 📋 Structured summary generation
- 🏅 Real-time class leaderboard
- 🗂️ Folder & tag-based content management
- 📊 Per-topic analytics & weakness reports

</td>
</tr>
</table>

<br/>

<div align="center">
<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/colored.png" width="100%" />
</div>

## 🏗️ Architecture

<div align="center">

```mermaid
flowchart TD
    subgraph INPUT["📥 Input Layer"]
        U[👤 User] -->|Upload PDF| API[⚡ FastAPI Router]
        U -->|Ask Question| API
    end

    subgraph PROCESSING["⚙️ Processing Pipeline"]
        API --> Parser["📄 Parser<br/>PyMuPDF / Docling / OCR"]
        Parser --> Normalizer["🧹 Cleaning & Normalizer"]
        Normalizer --> Chunker["✂️ Hierarchical Chunker"]
    end

    subgraph INDEXING["💾 Dual Index Storage"]
        Chunker --> Embedder["🧠 MiniLM-L6 Embedder"]
        Embedder --> FAISS["🔷 FAISS Vector Index"]
        Chunker --> BM25["🟢 BM25 Keyword Index"]
    end

    subgraph RETRIEVAL["🔍 Hybrid Retrieval"]
        FAISS --> RRF["⚡ RRF Fusion"]
        BM25 --> RRF
        RRF --> Reranker["🎯 Conditional Reranker"]
        Reranker --> MMR["🔀 MMR Diversity Filter"]
    end

    subgraph GENERATION["🤖 Grounded Generation"]
        MMR --> Context["📋 Token-Budgeted Context"]
        Context --> LLM["💎 Sarvam-M LLM"]
        LLM --> Trust["🛡️ Trust Layer"]
    end

    subgraph OUTPUT["📤 Output"]
        Trust --> Response["✅ Grounded Answer<br/>+ Source + Confidence"]
    end

    style INPUT fill:#1e3a5f,stroke:#60a5fa,color:#fff
    style PROCESSING fill:#1e3a5f,stroke:#60a5fa,color:#fff
    style INDEXING fill:#064e3b,stroke:#34d399,color:#fff
    style RETRIEVAL fill:#4c1d95,stroke:#a78bfa,color:#fff
    style GENERATION fill:#78350f,stroke:#fbbf24,color:#fff
    style OUTPUT fill:#14532d,stroke:#4ade80,color:#fff
```

</div>

<br/>

## 🚀 Core Features

<table>
<tr>
<td align="center" width="33%">

### 🤖 Grounded RAG (Trust-first)
<img src="https://img.shields.io/badge/12--step-ingestion-blue?style=flat-square" />
<img src="https://img.shields.io/badge/13--step-query-purple?style=flat-square" />

---
End-to-end grounded Q&A with strict constraints + citations + confidence. Low confidence → safe fallback.

</td>
<td align="center" width="33%">

### 🔍 Search Engine (Google-like UX)
<img src="https://img.shields.io/badge/FAISS-vector-blue?style=flat-square" />
<img src="https://img.shields.io/badge/BM25-keyword-green?style=flat-square" />

---
Keyword / Hybrid / AI / Auto routing + autocomplete suggestions from PDF vocabulary + "Did you mean?" typo correction.

</td>
<td align="center" width="33%">

### 🎯 Smart Reranker
<img src="https://img.shields.io/badge/LLM-conditional--reranker-orange?style=flat-square" />
<img src="https://img.shields.io/badge/conditional-skip-green?style=flat-square" />

---
LLM-based reranking only when needed (score gap < 0.02). Conditional skip saves latency on confident queries while boosting precision on ambiguous results.

</td>
</tr>
<tr>
<td align="center" width="33%">

### 📝 Quiz Engine
<img src="https://img.shields.io/badge/MCQ-auto--generated-yellow?style=flat-square" />
<img src="https://img.shields.io/badge/mock-tests-red?style=flat-square" />

---
LLM-generated quizzes from document content. Flashcards, mock tests, instant grading.

</td>
<td align="center" width="33%">

### 📊 Weakness Detection
<img src="https://img.shields.io/badge/per--topic-tracking-cyan?style=flat-square" />
<img src="https://img.shields.io/badge/adaptive-recs-purple?style=flat-square" />

---
Tracks per-topic quiz accuracy. Identifies weak areas. Generates targeted study recommendations.

</td>
<td align="center" width="33%">

### 📚 Content Library
<img src="https://img.shields.io/badge/auto-classify-blue?style=flat-square" />
<img src="https://img.shields.io/badge/subject-folders-green?style=flat-square" />

---
Unified hierarchy stored in SQLite (Subject → Unit → Topic → Subtopic). Used by both Library and the Course View reader.

</td>
</tr>
<tr>
<td align="center" width="33%">

### 🏆 Gamification
<img src="https://img.shields.io/badge/XP-system-gold?style=flat-square" />
<img src="https://img.shields.io/badge/levels-leaderboard-red?style=flat-square" />

---
Earn XP for quizzes and activities. Level up. Real-time leaderboard with cached performance.

</td>
<td align="center" width="33%">

### 🛡️ Trust Layer
<img src="https://img.shields.io/badge/confidence-scoring-green?style=flat-square" />
<img src="https://img.shields.io/badge/source-citations-blue?style=flat-square" />

---
Every answer includes confidence score + source page/section. Low confidence → "Not in document."

</td>
<td align="center" width="33%">

### 📈 Evaluation Engine
<img src="https://img.shields.io/badge/50+-test--cases-orange?style=flat-square" />
<img src="https://img.shields.io/badge/Recall%40k-MRR-purple?style=flat-square" />

---
Built-in evaluation: Recall@k, MRR, accuracy, hallucination rate. Ablation study ready.

</td>
</tr>
</table>

<br/>

<div align="center">
<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/aqua.png" width="100%" />
</div>

## 🔬 Tech Stack

<div align="center">

| Layer | Technology | Badge |
|:---:|:---:|:---:|
| **Backend** | FastAPI + Uvicorn | ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white) |
| **LLM** | Sarvam-M (105B / 30B) | ![AI](https://img.shields.io/badge/Sarvam--M-FF6B35?style=flat-square&logo=openai&logoColor=white) |
| **Embeddings** | sentence-transformers (MiniLM-L6-v2) | ![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat-square&logo=pytorch&logoColor=white) |
| **Vector DB** | FAISS (facebook) | ![Meta](https://img.shields.io/badge/FAISS-4285F4?style=flat-square&logo=meta&logoColor=white) |
| **Keyword** | BM25 (custom implementation) | ![Search](https://img.shields.io/badge/BM25-2ecc71?style=flat-square&logo=elasticsearch&logoColor=white) |
| **Database** | SQLite + SQLAlchemy 2.0 | ![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white) |
| **PDF** | PyMuPDF + Docling + OCR | ![PDF](https://img.shields.io/badge/PyMuPDF-FA0F00?style=flat-square&logo=adobeacrobatreader&logoColor=white) |
| **Frontend** | Vanilla JS + CSS (SPA) | ![JS](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black) |
| **HTTP** | httpx (async) | ![HTTP](https://img.shields.io/badge/httpx-async-blue?style=flat-square) |
| **Excel** | openpyxl | ![Excel](https://img.shields.io/badge/openpyxl-217346?style=flat-square&logo=microsoftexcel&logoColor=white) |

</div>

<br/>

## 🧠 Course View (NPTEL/Coursera-like) — unified hierarchy

When a PDF is uploaded, the backend generates **one persistent hierarchy** and stores it in SQLite.
Both the **Library** and the **Course View reader page** reuse the same hierarchy.

Example:

```text
Subject: Operating Systems
  Unit 1: Processes
    Topic: CPU Scheduling
      Subtopic: Round Robin Scheduling
        Content: page-aware text (used by Summarize/Explain + chat)
```

Course View UX:
- **Left sidebar**: collapsible tree (auto-expands to selected node)
- **Main panel**: content for the selected node
- **AI actions**: Summarize / Explain scoped to that section
- **Floating mentor**: chat prioritizes current section, then full document

## 🔄 How It Works

<div align="center">

```mermaid
flowchart LR
    subgraph UPLOAD["📤 Upload"]
        A["📄 PDF/Excel"] --> B["🔍 Parse"]
    end
    
    subgraph PROCESS["⚙️ Process"]
        B --> C["🧹 Clean"]
        C --> D["✂️ Chunk"]
        D --> E["🧠 Embed"]
    end
    
    subgraph INDEX["💾 Index"]
        E --> F["🔷 FAISS"]
        D --> G["🟢 BM25"]
    end
    
    subgraph QUERY["❓ Query"]
        H["🗣️ User Question"] --> I["🧭 Router"]
        I --> J["⚡ Hybrid Search"]
        F --> J
        G --> J
    end
    
    subgraph ANSWER["✅ Answer"]
        J --> K["🎯 Rerank + MMR"]
        K --> L["🤖 Sarvam-M"]
        L --> M["📝 Grounded Answer"]
    end

    style UPLOAD fill:#1e40af,stroke:#60a5fa,color:#fff
    style PROCESS fill:#065f46,stroke:#34d399,color:#fff
    style INDEX fill:#7c2d12,stroke:#fb923c,color:#fff
    style QUERY fill:#4c1d95,stroke:#a78bfa,color:#fff
    style ANSWER fill:#14532d,stroke:#4ade80,color:#fff
```

</div>

<br/>

## 📑 12-Step Ingestion Pipeline (Deep Dive)

Every uploaded document goes through these stages before it's ready for retrieval:

| Step | Stage | Description |
|:---:|:---|:---|
| 1 | **File Input** | Accept PDF or Excel via REST API upload |
| 2 | **Parser Routing** | Auto-detect format → PyMuPDF (fast), Docling (complex), OCR (scanned) |
| 3 | **Raw Extraction** | Extract raw text, layout blocks, and tables |
| 4 | **Cleaning Pipeline** | Remove headers/footers, fix broken lines, normalize whitespace |
| 5 | **Structure Builder** | Convert to section-based hierarchy: H1 → H2 → H3 |
| 6 | **Structured JSON** | `{ doc_id, sections: [{ heading, level, content, page }] }` |
| 7 | **Hierarchical Chunking** | Parent layer (section summary) + child layer (paragraph chunks) |
| 8 | **Adaptive Sizing** | < 100 words → merge · 200–350 → ideal · > 500 → split |
| 9 | **Table Processing** | Convert tables → `Entity → Attribute → Value` structured text |
| 10 | **Metadata Injection** | Attach `doc_id`, `section`, `page`, `level`, `type` to each chunk |
| 11 | **Embedding Generation** | `text → 384-dim vector` via MiniLM-L6-v2 |
| 12 | **Dual Indexing** | Store into FAISS (vector) + BM25 (keyword) + SQLite (metadata) |

<br/>

## 🔎 13-Step Query Pipeline (Deep Dive)

Every user question goes through this real-time retrieval pipeline:

| Step | Stage | Description |
|:---:|:---|:---|
| 1 | **User Input** | Accept keyword, question, or conceptual query |
| 2 | **Query Classification** | Classify as factual / conceptual / multi-hop |
| 3 | **Query Routing** | Route to optimal retrieval strategy per query type |
| 4 | **Query Expansion** | Generate 2–3 query variations for better recall |
| 5 | **FAISS Vector Search** | Semantic search → top-k by cosine similarity |
| 6 | **BM25 Keyword Search** | Exact keyword match → top-k by term frequency |
| 7 | **RRF Hybrid Fusion** | Merge rankings via `score = 1/(k + rank)` with dynamic weights |
| 8 | **Candidate Pool** | Produce top 20–30 candidate chunks |
| 9 | **Conditional Reranking** | If confidence gap > threshold → apply BGE cross-encoder |
| 10 | **MMR Diversity** | Remove near-duplicates (threshold 0.85), ensure topical coverage |
| 11 | **Token-Budgeted Context** | Select best chunks within 1500-token budget |
| 12 | **LLM Generation** | Sarvam-M generates answer from filtered context + strict prompt |
| 13 | **Trust Layer** | Attach confidence score + citations; low confidence → safe fallback |

<br/>

## 🔥 Retrieval — RRF Fusion Formula

```python
# Reciprocal Rank Fusion — merges vector + keyword rankings
rrf_score(chunk) = vector_weight × 1/(rrf_k + vector_rank)
                 + bm25_weight  × 1/(rrf_k + bm25_rank)
```

| Query Type | Vector Weight | BM25 Weight | Strategy |
|:---:|:---:|:---:|:---|
| 🎯 Factual | `0.3` | `0.7` | BM25-heavy — exact term match |
| 💡 Conceptual | `0.7` | `0.3` | Vector-heavy — semantic similarity |
| 🔗 Multi-hop | `0.5` | `0.5` | Balanced + multi-query expansion |

<br/>

## ⚡ Performance

| Metric | Value |
|:---|:---:|
| 🔍 BM25 Only | ~20ms |
| 🧠 Vector Only | ~30ms |
| ⚡ Hybrid RRF | ~60ms |
| 🎯 + Conditional Reranker | ~120–400ms |
| 🔀 + MMR Diversity | ~150–450ms |

<br/>

## 🔍 Search modes (with examples)

- **Keyword (BM25)**: best for exact terms like "process control block"
- **Hybrid (BM25 + FAISS via RRF)**: best for mixed queries like "why round robin increases context switches"
- **AI**: hybrid + (optional rerank) + grounded answer (sources + confidence)
- **Auto**: routes by query length/complexity

Example API call:

```bash
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d "{\"doc_id\":\"doc_x\",\"query\":\"process control block\",\"mode\":\"hybrid\",\"user_id\":\"default_user\"}"
```

<div align="center">
<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/fire.png" width="100%" />
</div>

## 🏆 Gamification & XP System

The platform incentivizes continuous learning through a robust gamification layer:

| Action | XP Earned |
|:---|:---:|
| 📤 Upload a document | +20 XP |
| 🤖 Ask AI a question | +5 XP |
| 📝 Complete a quiz | +50 XP |
| ✅ Each correct answer | +10 XP |
| 🔥 Daily login streak | +30 XP |

**Level Progression**: XP thresholds determine student levels, displayed on a real-time leaderboard with cached rankings for instant load.

<br/>

## 🛡️ Trust & Confidence System

The trust layer prevents hallucination and ensures answer reliability:

```
┌──────────────────────────────────────────────────┐
│  Confidence Score Calculation                    │
│                                                  │
│  Based on:                                       │
│  • Retrieval relevance scores                    │
│  • Reranker confidence                           │
│  • Agreement between top chunks                  │
│                                                  │
│  ┌────────────┬──────────┬─────────────────────┐ │
│  │  Score      │ Level    │ Action              │ │
│  ├────────────┼──────────┼─────────────────────┤ │
│  │  > 0.80    │ 🟢 High  │ Return full answer  │ │
│  │  0.25–0.80 │ 🟡 Med   │ Answer + disclaimer │ │
│  │  < 0.25    │ 🔴 Low   │ "Not in document"   │ │
│  └────────────┴──────────┴─────────────────────┘ │
└──────────────────────────────────────────────────┘
```

<br/>

## 📦 Project Structure

```
iveri-llm-advanced-rag-learning-system/
├── 📂 backend/
│   ├── 📂 app/
│   │   ├── 🚀 main.py                 ← FastAPI app + lifespan (startup/shutdown)
│   │   ├── ⚙️ config.py               ← All environment config + tuning knobs
│   │   ├── 🧠 state.py                ← Shared in-memory state (indexes, caches)
│   │   ├── 🗄️ database.py             ← SQLAlchemy 2.0 ORM models & sessions
│   │   │
│   │   ├── 📂 api/routes.py           ← All REST endpoints (~60KB, 40+ routes)
│   │   ├── 📂 parser/                 ← PyMuPDF / Docling / OCR parsers
│   │   ├── 📂 chunking/              ← Hierarchical chunker + adaptive sizing
│   │   ├── 📂 rag/                    ← Embedder, FAISS store, LLM client, retriever
│   │   ├── 📂 indexing/              ← Vector + BM25 index builders
│   │   ├── 📂 retrieval/             ← Hybrid RRF fusion + MMR diversity
│   │   ├── 📂 reranker/              ← Conditional BGE cross-encoder reranker
│   │   ├── 📂 query/                 ← Query classifier, router & expander
│   │   ├── 📂 llm/trust.py           ← Confidence scoring + citation extraction
│   │   ├── 📂 evaluation/            ← 50+ test suite + metrics engine
│   │   ├── 📂 generators/            ← Prompt templates (v4) for all tasks
│   │   ├── 📂 personalization/       ← Weakness detection + recommendations
│   │   ├── 📂 gamification/          ← XP engine + level system + leaderboard
│   │   ├── 📂 search/                ← Search engine layer (keyword/hybrid/AI)
│   │   ├── 📂 core/                  ← LLM classifier + content library manager
│   │   └── 📂 tasks/                 ← Background workers + pipeline queue pool
│   │
│   ├── 📂 frontend/
│   │   ├── 🌐 index.html             ← SPA shell (auth + all views)
│   │   ├── ⚡ app.js                  ← Full app logic (~92KB)
│   │   ├── 🎨 styles.css             ← Premium UI (~44KB)
│   │   ├── 📖 course.html/js/css     ← NPTEL-like course reader
│   │   ├── 🔍 search.html/js/css     ← Standalone search page
│   │   ├── 📄 pdf-viewer.html        ← In-browser PDF viewer
│   │   └── 🎨 favicon.svg            ← App icon
│   │
│   ├── 📋 requirements.txt
│   └── 📂 storage/                    ← FAISS + BM25 indexes + uploads
│
├── 📂 docs/                            ← Technical documentation
│   ├── about.md                       ← System identity & architecture layers
│   ├── features.md                    ← Complete feature catalog
│   └── flows.md                       ← System / data / user flow reference
│
├── 📄 .env.example                     ← Environment variable template
├── 📄 .gitignore
└── 📄 README.md                        ← You are here
```

<br/>

## 📡 API Endpoints Reference

The system exposes **40+ REST endpoints** via FastAPI. Here are the key endpoint groups:

<details>
<summary><strong>📤 Document Management</strong></summary>

| Method | Endpoint | Description |
|:---:|:---|:---|
| `POST` | `/api/upload` | Upload PDF/Excel for processing |
| `GET` | `/api/documents` | List all uploaded documents |
| `DELETE` | `/api/documents/{doc_id}` | Delete a document and its indexes |
| `GET` | `/api/status/{doc_id}` | Check ingestion pipeline status |

</details>

<details>
<summary><strong>🤖 AI & RAG</strong></summary>

| Method | Endpoint | Description |
|:---:|:---|:---|
| `POST` | `/api/ask` | Ask AI a question (full RAG pipeline) |
| `POST` | `/api/search` | Search documents (keyword/hybrid/AI) |
| `POST` | `/api/summarize` | Generate section/document summary |
| `POST` | `/api/explain` | Get AI explanation for a topic |

</details>

<details>
<summary><strong>📝 Quiz & Learning</strong></summary>

| Method | Endpoint | Description |
|:---:|:---|:---|
| `POST` | `/api/quiz/generate` | Generate MCQ quiz from content |
| `POST` | `/api/quiz/submit` | Submit quiz answers for grading |
| `POST` | `/api/mock-test/generate` | Generate full mock test |
| `POST` | `/api/flashcards/generate` | Generate flashcard set |

</details>

<details>
<summary><strong>📊 Analytics & Personalization</strong></summary>

| Method | Endpoint | Description |
|:---:|:---|:---|
| `GET` | `/api/weakness/{user_id}` | Get weak topics analysis |
| `GET` | `/api/recommendations/{user_id}` | Get study recommendations |
| `GET` | `/api/leaderboard` | Get XP leaderboard |
| `GET` | `/api/progress/{user_id}` | Get user learning progress |

</details>

<details>
<summary><strong>📚 Content Library</strong></summary>

| Method | Endpoint | Description |
|:---:|:---|:---|
| `GET` | `/api/library/subjects` | List all subjects |
| `POST` | `/api/library/classify` | Auto-classify document into subject |
| `GET` | `/api/library/hierarchy/{doc_id}` | Get course view hierarchy |
| `DELETE` | `/api/library/document/{doc_id}` | Remove document from library |

</details>

<br/>

## ⚙️ Configuration Reference

All configuration is managed through environment variables and `config.py`:

<details>
<summary><strong>🔧 Environment Variables (.env)</strong></summary>

| Variable | Default | Description |
|:---|:---|:---|
| `SARVAM_API_KEY` | *(required)* | API key for Sarvam LLM |
| `SARVAM_API_URL` | `https://api.sarvam.ai/v1/chat/completions` | LLM API endpoint |
| `SARVAM_MODEL_105B` | `sarvam-105b` | Large model ID |
| `SARVAM_MODEL_30B` | `sarvam-30b` | Fast model ID |
| `LLM_TEMPERATURE` | `0.2` | Default generation temperature |
| `LLM_TIMEOUT_SECONDS` | `120` | Request timeout |

</details>

<details>
<summary><strong>🎛️ RAG Pipeline Tuning</strong></summary>

| Parameter | Value | Purpose |
|:---|:---:|:---|
| `CHUNK_SIZE_WORDS` | 350 | Target chunk size |
| `CHUNK_OVERLAP_WORDS` | 50 | Overlap between chunks |
| `CHUNK_MIN_WORDS` | 100 | Merge threshold |
| `CHUNK_MAX_WORDS` | 500 | Split threshold |
| `MAX_CONTEXT_TOKENS` | 1500 | LLM context budget |
| `RRF_K_DEFAULT` | 10 | RRF fusion constant |
| `MMR_LAMBDA` | 0.7 | Relevance vs diversity |
| `MMR_SIMILARITY_THRESHOLD` | 0.85 | Near-duplicate detection |
| `RERANK_MIN_CANDIDATES` | 5 | Minimum for reranking |
| `RERANK_SCORE_GAP` | 0.02 | Confidence gap trigger |
| `CONFIDENCE_FALLBACK_THRESHOLD` | 0.25 | Below this → safe fallback |

</details>

<details>
<summary><strong>🏆 Gamification XP Values</strong></summary>

| Action | XP |
|:---|:---:|
| Upload document | 20 |
| Ask AI question | 5 |
| Complete quiz | 50 |
| Correct answer | 10 |
| Daily streak | 30 |

</details>

<br/>

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/Nishant-aiml/iveri-llm-advanced-rag-learning-system.git
cd iveri-llm-advanced-rag-learning-system

# 2. Setup
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac

# 3. Install
pip install -r requirements.txt

# 4. Configure (.env file)
cp .env.example .env
# then edit .env and set SARVAM_API_KEY

# 5. Run
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

<div align="center">

| Interface | URL |
|:---:|:---:|
| 🌐 **Web App** | `http://localhost:8000` |
| 📖 **Swagger API** | `http://localhost:8000/docs` |
| 📄 **ReDoc** | `http://localhost:8000/redoc` |
| 📚 **Course View** | `http://localhost:8000/course.html` |
| 🔍 **Search** | `http://localhost:8000/search.html` |

</div>

<br/>

### 🐳 Docker (Optional)

```bash
# Build
docker build -t iveri-llm .

# Run
docker run -p 8000:8000 --env-file .env iveri-llm
```

<br/>

## 📊 Evaluation & Metrics

> **Method**: `evaluation/run_evaluation.py` | **Dataset**: 60 queries (20 factual, 20 conceptual, 10 multi-hop, 10 adversarial) | **Ground Truth**: Independent manual chunk-ID mappings

### Retrieval Quality

| Metric | Value |
|:---|:---:|
| **Recall@3** | 0.615 |
| **Recall@5** | 0.730 |
| **MRR** | 0.791 |
| Avg Semantic Similarity | 0.608 |
| Key Term Coverage | 51.9% |
| Hallucination Rate | **4.0%** |
| Not-Found Accuracy | **70.0%** |

### Baseline vs Hybrid Comparison

| System | Recall@3 | Recall@5 | MRR |
|:---|:---:|:---:|:---:|
| Baseline (Vector-Only) | 0.593 | 0.700 | 0.781 |
| **Hybrid (FAISS + BM25 + RRF)** | **0.615** | **0.730** | **0.791** |
| Δ Improvement | +3.7% | +4.3% | +1.3% |

### Confidence Calibration

```
confidence = 0.4 × norm_vector_score + 0.3 × norm_rrf_score + 0.3 × agreement_overlap
```

| Confidence Level | Count | Accuracy |
|:---|:---:|:---:|
| High (> 0.7) | 47 | **93.6%** |
| Medium (0.4–0.7) | 3 | — |

### Latency Breakdown (Retrieval-Only, excludes LLM)

| Stage | Avg | p50 | p95 |
|:---|:---:|:---:|:---:|
| Embedding | 22.6ms | — | — |
| Vector Search | 0.1ms | — | — |
| Hybrid (FAISS+BM25+RRF) | 73.5ms | — | — |
| **Total** | **96.1ms** | **87.5ms** | **166.4ms** |

> ⚠️ **Dataset caveat**: 60 queries on a single-domain Python textbook. Cross-domain generalization not tested. See `evaluation/reports/` for full data.

<br/>

## 🧪 Testing

The project includes multiple test suites:

```bash
# Quick sanity check
python test_quick.py

# End-to-end integration tests
python test_e2e.py

# Ingestion pipeline tests
python test_e2e_ingest.py

# Batching & partial upload tests
python test_e2e_batching_and_partial.py

# LLM response contract tests
python test_ai_strict_contracts.py

# LLM connectivity test
python test_llm.py
```

<br/>

## 🛣️ Roadmap

- [ ] 🔄 Streaming LLM responses (real-time)
- [ ] 🧬 Graph-based retrieval for multi-hop queries
- [ ] 📊 Teacher analytics dashboard
- [ ] 🌐 Multi-LLM support (OpenAI, Gemini, Ollama)
- [ ] 🔍 Elasticsearch for scalable keyword search
- [ ] 📱 Mobile-responsive redesign
- [ ] 🧠 Fine-tuned domain embeddings
- [ ] 🌍 Multi-language support (Hindi, regional languages via Sarvam)
- [ ] 📊 Advanced analytics with visualization charts
- [ ] 🔐 Role-based access control (Student / Teacher / Admin)
- [ ] 📤 Export quiz results as PDF/CSV reports

<br/>

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

Please ensure your code follows the existing patterns and include tests for new features.

<br/>

## ❓ FAQ

<details>
<summary><strong>What LLM does this use?</strong></summary>

IVERI LLM uses **Sarvam-M** (available in 105B and 30B variants), an Indian AI model optimized for multilingual understanding. You need a Sarvam API key to use the system. Toggle between models from the UI.

</details>

<details>
<summary><strong>Can I use OpenAI / Gemini / Ollama instead?</strong></summary>

Not yet — multi-LLM support is on the roadmap. The architecture is designed for easy LLM swapping via the `llm_client.py` abstraction layer.

</details>

<details>
<summary><strong>How large can uploaded PDFs be?</strong></summary>

Up to **20 MB** per file. The system supports PDF and Excel (`.xlsx`) formats. Scanned PDFs are handled via OCR fallback.

</details>

<details>
<summary><strong>Does it work offline?</strong></summary>

The embedding model and search (BM25 + FAISS) work fully offline. Only LLM generation (Q&A, quizzes, summaries) requires an internet connection to reach the Sarvam API.

</details>

<details>
<summary><strong>How is the hierarchy generated?</strong></summary>

The system uses heading detection (H1/H2/H3) from PyMuPDF parsing, supplemented by LLM-based classification to auto-generate a `Subject → Unit → Topic → Subtopic` hierarchy stored in SQLite.

</details>

<br/>

<div align="center">
<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%" />
</div>

## 🔬 Evaluation Integrity

### Ground Truth Independence

Each of the 50 non-adversarial queries is manually mapped to specific chunk IDs from the source document. These mappings are **independent of system output** — they represent which chunks _should_ be retrieved, not which chunks _were_ retrieved.

### Why This Evaluation Is Honest

1. **No self-referential ground truth** — we do NOT use the system's own output as reference
2. **Realistic improvement claims** — +4.3% Recall@5, not inflated percentages
3. **Failures documented** — 8/60 queries fail, with root cause categorization
4. **Confidence calibrated** — 93.6% accuracy at high confidence, not 100%
5. **Latency clearly scoped** — excludes LLM, measures retrieval-only pipeline

### Known Limitations

| Limitation | Impact |
|:---|:---|
| Small dataset (60 queries) | Insufficient for statistical significance |
| Single domain (Python textbook) | Cross-domain generalization unknown |
| No LLM answer quality metrics | Sarvam API unavailable during evaluation |
| Short chunks (avg 17.7 words) | Reduces embedding discriminative power |
| Adversarial threshold (0.25) | 30% false positive rate on out-of-scope queries |

### Reproducibility

```bash
cd backend
python evaluation/run_evaluation.py   # Regenerates all metrics from scratch
# Outputs: evaluation/reports/metrics.json, comparison.json, failures.md, trust_formula.md
```

> Full formula and calibration: `evaluation/reports/trust_formula.md`

<br/>

<div align="center">
<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%" />
</div>

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

<br/>

## 👨‍💻 Author

<div align="center">

| | |
|:---:|:---|
| 🧑‍💻 | **Nishant Datta** |
| 🏗️ | Lead Architect & Engineer |
| 🎯 | RAG Pipeline, Retrieval, Evaluation, Frontend |

<br/>

[![GitHub](https://img.shields.io/badge/GitHub-Nishant--aiml-181717?style=for-the-badge&logo=github)](https://github.com/Nishant-aiml)

</div>

<br/>

<div align="center">

> *"This is not a student project. This is a system."*

<br/>

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:1e3a5f,50:2563eb,100:7c3aed&height=120&section=footer" width="100%" />

</div>
