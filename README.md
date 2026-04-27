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

> **A hybrid Retrieval-Augmented Generation (RAG) pipeline** combining FAISS vector search, BM25 keyword indexing, and Reciprocal Rank Fusion — with measured Recall@5 improvement from 0.700 to 0.720 (~2.9%) over vector-only baseline, 95.7% confidence calibration accuracy, and evaluation across 2 datasets.

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
- 🎯 80-query multi-dataset evaluation engine
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
| 9 | **Conditional Reranking** | If confidence gap > threshold → apply LLM-based reranker |
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

> **Methodology**: Ablation study across 2 datasets (80 queries) with independent ground truth | **Source**: `evaluation/run_evaluation.py`

### How the System Works

The system uses **MiniLM-L6-v2** (embedding model) + **BM25** (keyword matching) **together** in a hybrid pipeline:

```
Query → MiniLM-L6-v2 embedding → FAISS vector search (semantic)
      → BM25 tokenization       → BM25 keyword search (exact match)
      → RRF Fusion (merges both ranked lists into one)
```

The evaluation is an **ablation study** — testing what happens when you disable one component:

### Ablation Results (Dataset A: Python Textbook — 60 queries, fully labeled)

| Configuration | Recall@3 | Recall@5 | MRR | Semantic Sim | Hallucination |
|:---|:---:|:---:|:---:|:---:|:---:|
| MiniLM only (FAISS) | 0.593 | 0.700 | 0.781 | 0.642 | 2.0% |
| BM25 only (keyword) | 0.567 | 0.655 | 0.800 | 0.570 | 8.0% |
| **MiniLM + BM25 + RRF** | **0.598** | **0.720** | **0.793** | **0.599** | **2.0%** |

### Cross-Domain Validation (Dataset B: AI/ML Notes — 20 queries, 18 labeled)

| Configuration | Recall@3 | Recall@5 | MRR | Semantic Sim | Hallucination |
|:---|:---:|:---:|:---:|:---:|:---:|
| MiniLM only (FAISS) | 0.833 | 0.889 | 0.880 | 0.692 | 0.0% |
| **MiniLM + BM25 + RRF** | **0.833** | **0.889** | **0.889** | **0.692** | **0.0%** |

> BM25-only shows 0 recall on Dataset B because no BM25 index was built for this document (uploaded before BM25 indexing was configured). BM25-only comparison is therefore limited to Dataset A. This is an honest limitation, not excluded data.

### Approximate Answer Correctness

| Metric | Dataset A | Dataset B | Combined |
|:---|:---:|:---:|:---:|
| Approx. Answer Correctness | 82.0% | 83.3% | **82.5%** |
| Semantic Similarity | 0.599 | 0.692 | 0.646 |
| Key Term Coverage | 50.4% | 44.7% | 47.6% |
| Hallucination Rate | 2.0% | 0.0% | 1.0% |

**Note**: Answer correctness is a heuristic estimate, not an exact semantic evaluation. Factual queries require ≥50% key term coverage in retrieved chunks; conceptual/multi-hop queries require ≥0.4 semantic similarity to the expected answer. This provides a practical approximation of answer quality without requiring LLM-based judging.

### Per-Query-Type Breakdown (Dataset A)

| Query Type | Count | Semantic Sim | Coverage | Accuracy |
|:---|:---:|:---:|:---:|:---:|
| Factual | 20 | 0.584 | 59.4% | 95.0% |
| Conceptual | 20 | 0.627 | 44.6% | 95.0% |
| Multi-hop | 10 | 0.575 | 44.0% | 100.0% |

### Confidence Calibration (Trust Layer)

```
confidence = 0.4 × norm_vector_score + 0.3 × norm_rrf_score + 0.3 × agreement_overlap
```

| Confidence | Threshold | Dataset A |  | Dataset B |  |
|:---|:---:|:---:|:---:|:---:|:---:|
|  |  | Count | Accuracy | Count | Accuracy |
| High | > 0.7 | 47 | **95.7%** | 17 | **94.1%** |
| Medium | 0.4–0.7 | 10 | 70.0% | 2 | 100.0% |
| Low | < 0.4 | 3 | 100.0% | 1 | 100.0% |

Confidence calibration is consistent across domains: ~95% of high-confidence answers contain relevant content in both datasets.

### Latency (Retrieval-Only, excludes LLM generation)

| Component | Avg | p50 | p95 |
|:---|:---:|:---:|:---:|
| MiniLM embedding | 22.6ms | — | — |
| FAISS vector search | 0.1ms | 0.0ms | 1.0ms |
| BM25 keyword search | 0.2ms | 0.0ms | 1.5ms |
| **Full hybrid pipeline** | **66.4ms** | **64.0ms** | **85.2ms** |

Hybrid latency (~66ms) is dominated by BM25 tokenization + RRF fusion. LLM generation (Sarvam-30B) adds ~500–2000ms.

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

## ⚖️ Comparison with RAG Architectures

| Architecture | Strength | Weakness | When It Fails |
|:---|:---|:---|:---|
| **BM25 only** | Fast exact keyword match | No semantic understanding | Conceptual queries, paraphrased questions |
| **MiniLM only** (Vector) | Semantic understanding, handles paraphrases | Misses exact technical terms | Keyword-specific queries, abbreviations |
| **MiniLM + BM25 + RRF** (Hybrid) | Captures both semantic + lexical signals | Higher latency (~66ms vs <1ms) | Heavy concurrent workloads |

### Measured Performance (Dataset A)

| Architecture | Recall@5 | MRR | Semantic Sim | Hallucination | Latency |
|:---|:---:|:---:|:---:|:---:|:---:|
| BM25 only | 0.655 | 0.800 | 0.570 | **8.0%** | 0.2ms |
| MiniLM only | 0.700 | 0.781 | **0.642** | 2.0% | 0.1ms |
| **Hybrid** | **0.720** | **0.793** | 0.599 | **2.0%** | 66.4ms |

**Improvement**: Hybrid Recall@5 (0.720) vs MiniLM-only (0.700) = **+2.9%**. Hybrid vs BM25-only (0.655) = **+9.9%**.

**Why hybrid improves recall**: RRF fusion combines both ranking signals. When a keyword query like "LEGB rule" doesn't match well semantically, BM25 catches it. When a conceptual query like "why does the GIL exist" needs meaning, MiniLM catches it.

**Why BM25 alone increases hallucination**: BM25 matches keywords without understanding context. A chunk containing the right words but wrong meaning gets ranked high, leading to 4× more hallucination (8% vs 2%).

> **Note**: BM25-only comparison is limited to Dataset A due to indexing constraints on Dataset B.

<br/>

## 📉 Tradeoffs in Hybrid Retrieval

The hybrid system optimizes **retrieval coverage**, not embedding similarity. This creates a measurable tradeoff:

| Metric | MiniLM Only | Hybrid | Interpretation |
|:---|:---:|:---:|:---:|
| Recall@5 | 0.700 | **0.720** | ↑ improved coverage |
| Semantic Sim | **0.642** | 0.599 | expected tradeoff |
| Hallucination | 2.0% | 2.0% | → maintained |
| Coverage | 49.7% | **50.4%** | ↑ improved coverage |

**Why semantic similarity shifts in hybrid mode**: BM25 introduces keyword-matched chunks that may not be the closest in embedding space but contain relevant factual content. This improves recall and coverage while producing a small similarity tradeoff (-0.043), which is a design-level choice: prioritizing retrieval coverage over embedding closeness.

**Interpretation**: The similarity tradeoff is expected and acceptable. The system retrieves more relevant chunks overall, which improves answer quality even though individual chunk similarity scores are slightly lower.

<br/>

## 🌐 Generalization Analysis

### Cross-Domain Performance

| Metric | Dataset A (Python) | Dataset B (AI/ML) | Consistent? |
|:---|:---:|:---:|:---:|
| Recall@5 | 0.720 | 0.889 | ✅ |
| Semantic Sim | 0.599 | 0.692 | ✅ |
| Approx. Correctness | 82.0% | 83.3% | ✅ |
| Trust (high-conf) | 95.7% | 94.1% | ✅ |
| Hallucination | 2.0% | 0.0% | ✅ |

**Analysis**: Results are consistent across two different domains (programming vs AI/ML theory). Both datasets show ~95% confidence calibration, ~82% approximate answer correctness, and low hallucination rates.

**Dataset B context**: Dataset B achieves higher recall (0.889 vs 0.720) because its source document has shorter, more focused chunks (21 vs 75 chunks). A smaller retrieval space naturally yields higher recall — this reflects document characteristics, not a difference in system quality. Both datasets demonstrate consistent confidence calibration (~95%), which is the stronger indicator of cross-domain robustness.

### Statistical Context

This evaluation uses **80 queries across 2 datasets** (60 + 20). Results are consistent across domains. At this sample size, improvements (e.g., +2.9% Recall@5) represent **directional evidence** of hybrid retrieval benefit. Larger-scale validation (500+ queries across 5+ domains) would strengthen confidence intervals for publication-grade claims.

<br/>

## 🔬 Evaluation Integrity

### Datasets

| Dataset | Domain | Queries | Labeled Queries | Ground Truth |
|:---|:---|:---:|:---:|:---|
| **A** (fully labeled) | Python programming | 60 | 50 | Manual chunk-ID mapping |
| **B** (partially labeled) | AI/ML fundamentals | 20 | 18 | Manual chunk-ID mapping |

### Ground Truth Independence

All chunk-ID mappings were created by inspecting document content and manually identifying which chunks should be retrieved for each query. These mappings are **independent of system output** — they define which chunks _should_ be retrieved, not which chunks _were_ retrieved.

### Failure Analysis

| Category | Count | Root Cause |
|:---|:---:|:---|
| Retrieval miss | 5 | Gold chunk not in top-5 (embedding similarity too low) |
| False positive | 3 | Adversarial query not rejected (score > 0.25 threshold) |
| Hallucination risk | 2 | Retrieved chunk has low similarity + low coverage |

Full details with per-query examples: `evaluation/reports/failures.md`

### Known Limitations

| Limitation | Impact | Mitigation |
|:---|:---|:---|
| Small dataset (80 queries) | Directional evidence, not statistical proof | Report exact counts alongside percentages |
| Two domains only | Generalization partially tested | Both show ~95% trust calibration |
| MiniLM-L6-v2 (384-dim) | Smaller embedding model | Adequate for educational content |
| Adversarial threshold (0.25) | 30% false positive rate | Threshold is configurable |
| No BM25 index for Dataset B | BM25-only comparison limited to Dataset A | Noted transparently in results |
| Hybrid latency (~66ms) | Higher than vector-only (0.1ms) | Sub-100ms p50, suitable for interactive use |

### Reproducibility

```bash
cd backend
python evaluation/run_evaluation.py   # Ablation × 2 datasets, ~3 min
# Outputs:
#   evaluation/reports/metrics.json      — all metrics
#   evaluation/reports/comparison.csv    — system comparison table
#   evaluation/reports/failures.md       — categorized failure analysis
#   evaluation/reports/trust_formula.md  — confidence formula + calibration
#   evaluation/logs/run.json             — per-query execution logs
```

<br/>

## 💬 Common Questions & Answers

<details>
<summary><strong>Q1: Why is the improvement only ~2.9%?</strong></summary>

The MiniLM vector baseline is already strong (Recall@5 = 0.700). At high baselines, each percentage point of improvement is harder to achieve. The hybrid system's +2.9% gain (0.700 → 0.720) comes from edge-case queries where exact keyword matching helps — these are the queries that would fail with vector-only search.

</details>

<details>
<summary><strong>Q2: Why does semantic similarity shift in hybrid mode?</strong></summary>

This is a design-level tradeoff. Hybrid retrieval prioritizes **coverage** over **embedding closeness**. BM25 introduces keyword-matched chunks that may not be the closest in embedding space but contain factually relevant content. The similarity tradeoff (0.642 → 0.599, Δ = -0.043) is expected and acceptable — recall improves because the system finds more correct chunks, and overall answer quality benefits from broader coverage.

</details>

<details>
<summary><strong>Q3: How does this generalize to other domains?</strong></summary>

Tested on 2 datasets (Python textbook + AI/ML notes). Both show consistent results: ~95% confidence calibration, ~82% approximate answer correctness, <2% hallucination. Dataset B's higher recall (0.889 vs 0.720) reflects its smaller retrieval space (21 vs 75 chunks), not superior performance. Confidence calibration consistency (~95% across both) is the stronger generalization signal. Larger-scale multi-domain testing would further strengthen these claims.

</details>

<details>
<summary><strong>Q4: How do you evaluate answer correctness?</strong></summary>

Four complementary metrics: (1) **Recall@k** measures whether correct chunks are retrieved, (2) **Semantic similarity** compares retrieved text to expected answers, (3) **Key term coverage** checks if important terms appear in results, (4) **Hallucination rate** flags answers with low similarity AND low coverage. Note that "Approximate Answer Correctness" (82.5%) is a heuristic estimate using coverage and similarity thresholds, not an exact LLM-judged evaluation.

</details>

<details>
<summary><strong>Q5: Why not just use vector search?</strong></summary>

Vector search misses exact keywords. A query like "LEGB rule" may not match semantically if the embedding doesn't capture the acronym. BM25 catches these through direct keyword matching. The hybrid system recovers ~3 additional correct chunks per 100 queries that vector-only misses.

</details>

<details>
<summary><strong>Q6: What are the system's limitations?</strong></summary>

- **Evaluation scale**: 80 queries across 2 datasets — provides directional evidence; larger datasets would strengthen claims
- **Load testing**: Hybrid latency (~66ms) measured locally; concurrent load behavior not yet profiled
- **Single embedding model**: MiniLM-L6-v2 (384-dim) — adequate for educational content; larger models may further improve recall
- **Single-server deployment**: Not yet tested in distributed environments
- **LLM dependency**: Answer generation requires external Sarvam API; retrieval pipeline works fully offline

</details>

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

> *This project emphasizes evaluation-driven system design — measurable improvements, transparent tradeoffs, and reproducible benchmarking over raw feature complexity.*

<br/>

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:1e3a5f,50:2563eb,100:7c3aed&height=120&section=footer" width="100%" />

</div>
