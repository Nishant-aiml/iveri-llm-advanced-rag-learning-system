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

<br/>

> **A production-grade Retrieval-Augmented Generation (RAG) pipeline** combining hybrid information retrieval, multi-stage reranking, grounded LLM generation, and evaluation-driven optimization — delivering a personalized AI learning and student monitoring platform.

<br/>

<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%" />

</div>

## ⚡ Quick Overview

```
📄 Upload a Document  →  🧠 AI Processes & Indexes  →  🎯 Ask, Search, Quiz, Learn
```

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

</td>
<td width="50%">

### 👨‍🏫 For Educators
- 📚 Subject-based Content Library
- 🔄 LLM Auto-Classification of documents
- 📈 Student performance monitoring
- 🎯 50+ question evaluation engine
- 📋 Structured summary generation
- 🏅 Real-time class leaderboard

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
        Chunker --> Embedder["🧠 BGE Embedder"]
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

### 🤖 RAG Pipeline
<img src="https://img.shields.io/badge/12--step-ingestion-blue?style=flat-square" />
<img src="https://img.shields.io/badge/13--step-query-purple?style=flat-square" />

---
End-to-end grounded Q&A with strict prompt constraints. Chain-of-thought cleanup. Zero hallucination by design.

</td>
<td align="center" width="33%">

### 🔍 Hybrid Search
<img src="https://img.shields.io/badge/FAISS-vector-blue?style=flat-square" />
<img src="https://img.shields.io/badge/BM25-keyword-green?style=flat-square" />

---
Parallel vector + keyword search with RRF fusion. Dynamic weight routing per query type. Google-like UI.

</td>
<td align="center" width="33%">

### 🎯 Smart Reranker
<img src="https://img.shields.io/badge/BGE-cross--encoder-orange?style=flat-square" />
<img src="https://img.shields.io/badge/conditional-skip-green?style=flat-square" />

---
Cross-encoder reranking only when needed. Saves 150-300ms on confident queries while boosting precision.

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
LLM auto-classifies uploaded documents into subject folders. Tag, view, delete, organize.

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
| **LLM** | Sarvam-M (HTTP API) | ![AI](https://img.shields.io/badge/Sarvam--M-FF6B35?style=flat-square&logo=openai&logoColor=white) |
| **Embeddings** | sentence-transformers (BGE) | ![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat-square&logo=pytorch&logoColor=white) |
| **Vector DB** | FAISS (facebook) | ![Meta](https://img.shields.io/badge/FAISS-4285F4?style=flat-square&logo=meta&logoColor=white) |
| **Keyword** | BM25 (custom) | ![Search](https://img.shields.io/badge/BM25-2ecc71?style=flat-square&logo=elasticsearch&logoColor=white) |
| **Database** | SQLite + SQLAlchemy 2.0 | ![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white) |
| **PDF** | PyMuPDF + Docling + OCR | ![PDF](https://img.shields.io/badge/PyMuPDF-FA0F00?style=flat-square&logo=adobeacrobatreader&logoColor=white) |
| **Frontend** | Vanilla JS + CSS (SPA) | ![JS](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black) |
| **HTTP** | httpx (async) | ![HTTP](https://img.shields.io/badge/httpx-async-blue?style=flat-square) |

</div>

<br/>

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

<div align="center">
<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/fire.png" width="100%" />
</div>

## 📦 Project Structure

```
timepass/
├── 📂 backend/
│   ├── 📂 app/
│   │   ├── 🚀 main.py                 ← FastAPI app + lifespan
│   │   ├── ⚙️ config.py               ← All environment config
│   │   ├── 🧠 state.py                ← Shared in-memory state
│   │   ├── 🗄️ database.py             ← SQLAlchemy ORM
│   │   │
│   │   ├── 📂 api/routes.py           ← All REST endpoints
│   │   ├── 📂 parser/                 ← PyMuPDF / Docling / OCR
│   │   ├── 📂 chunking/              ← Hierarchical chunker
│   │   ├── 📂 rag/                    ← Embedder, FAISS, LLM client
│   │   ├── 📂 indexing/              ← Vector + BM25 indexes
│   │   ├── 📂 retrieval/             ← Hybrid RRF + MMR
│   │   ├── 📂 reranker/              ← Conditional BGE reranker
│   │   ├── 📂 query/                 ← Router + Expander
│   │   ├── 📂 llm/trust.py           ← Confidence + Citations
│   │   ├── 📂 evaluation/            ← 50+ test suite
│   │   ├── 📂 generators/            ← Prompt templates
│   │   ├── 📂 personalization/       ← Weakness detection
│   │   ├── 📂 gamification/          ← XP + Leaderboard
│   │   ├── 📂 search/                ← Search engine layer
│   │   ├── 📂 core/                  ← Classifier + Library
│   │   └── 📂 tasks/                 ← Background workers
│   │
│   ├── 📂 frontend/
│   │   ├── 🌐 index.html             ← SPA shell
│   │   ├── ⚡ app.js                  ← Full app logic (~61KB)
│   │   └── 🎨 styles.css             ← Premium UI (~40KB)
│   │
│   └── 📋 requirements.txt
│
└── 📂 storage/                        ← FAISS + BM25 indexes
```

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
echo SARVAM_API_KEY=your_key_here > .env
echo SARVAM_API_URL=https://api.sarvam.ai/v1/chat/completions >> .env

# 5. Run
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

<div align="center">

| Interface | URL |
|:---:|:---:|
| 🌐 **Web App** | `http://localhost:8000` |
| 📖 **Swagger API** | `http://localhost:8000/docs` |
| 📄 **ReDoc** | `http://localhost:8000/redoc` |

</div>

<br/>

## 📊 Evaluation & Metrics

| Metric | Description |
|:---|:---|
| **Recall@k** | Fraction of relevant chunks in top-k results |
| **MRR** | Mean Reciprocal Rank of first relevant chunk |
| **Answer Accuracy** | LLM answer correctness vs ground truth |
| **Hallucination Rate** | % of answers with ungrounded content |
| **Latency (p50/p95)** | End-to-end response time |

### Ablation Study

| Configuration | Recall@5 | MRR | Accuracy |
|:---|:---:|:---:|:---:|
| Vector-only baseline | 🟡 Low | 🟡 Low | 🟡 Medium |
| + BM25 Hybrid (RRF) | 🟢 Higher | 🟢 Higher | 🟢 Better |
| + Conditional Reranker | 🔵 High | 🔵 High | 🔵 High |
| + Query Expansion | 🟣 **Best** | 🟣 **Best** | 🟣 **Best** |

<br/>

## 🛣️ Roadmap

- [ ] 🔄 Streaming LLM responses (real-time)
- [ ] 🧬 Graph-based retrieval for multi-hop queries
- [ ] 📊 Teacher analytics dashboard
- [ ] 🌐 Multi-LLM support (OpenAI, Gemini, Ollama)
- [ ] 🔍 Elasticsearch for scalable keyword search
- [ ] 📱 Mobile-responsive redesign
- [ ] 🧠 Fine-tuned domain embeddings

<br/>

<div align="center">
<img src="https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png" width="100%" />
</div>

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
