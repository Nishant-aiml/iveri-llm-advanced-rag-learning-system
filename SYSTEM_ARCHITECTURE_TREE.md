# 🏗️ SYSTEM_ARCHITECTURE_TREE.md — IVERI LLM Enterprise AI Learning Platform

This document presents the full, detailed architecture tree of the IVERI LLM system.

---

## 1. High-Level Architectural Tree

```text
c:\Users\datta.000\Desktop\internship project
├── backend/
│   ├── app/
│   │   ├── api/                   # Legacy Monolithic API Layer
│   │   │   └── routes.py          # Legacy HTTP routes/handlers (1,600+ lines)
│   │   │
│   │   ├── feature_registry.py    # Centralized Registry for System Features
│   │   ├── features/              # Modularized Business-Logic Domain Layer
│   │   │   ├── grounded_rag/
│   │   │   ├── search_engine/
│   │   │   ├── smart_reranker/
│   │   │   ├── quiz_engine/
│   │   │   ├── weakness_detection/
│   │   │   ├── content_library/
│   │   │   ├── gamification/
│   │   │   ├── trust_layer/
│   │   │   ├── evaluation_engine/
│   │   │   ├── llm_platform/
│   │   │   ├── ingestion_pipeline/
│   │   │   ├── course_system/
│   │   │   ├── analytics/
│   │   │   └── shared/
│   │   │
│   │   ├── modules/               # Feature-Specific Routes + Domain Services
│   │   │   ├── ask_ai/            # Grounded Q&A API
│   │   │   ├── auth/              # Registration, Login, JWT
│   │   │   ├── analytics/         # Usage tracking API
│   │   │   ├── content_library/   # Multi-PDF organization
│   │   │   ├── courses/           # Course syllabus & content generator
│   │   │   ├── evaluation/        # Retrieval/LLM validation endpoints
│   │   │   ├── flashcards/        # Study cards generator
│   │   │   ├── gamification/      # XP, Levels, Leaderboards
│   │   │   ├── llm_router/        # Multi-provider chat wrappers
│   │   │   ├── quizzes/           # MCQ generation & submission
│   │   │   ├── search_engine/     # Search & spell suggestions
│   │   │   ├── upload_pipeline/   # PDF chunk & index execution
│   │   │   └── weaknesses/        # Personalization dashboard APIs
│   │   │
│   │   ├── shared/                # Core Shared Infrastructure Layer
│   │   │   ├── caching/           # Memory stores & locks
│   │   │   ├── database/          # SQLAlchemy connections & metadata
│   │   │   ├── schemas/           # Global Pydantic shapes
│   │   │   ├── storage/           # Disk storage path configurations
│   │   │   └── utils/             # Document handling & general helpers
│   │   │
│   │   ├── core/                  # Core Legacy Algorithms & Services
│   │   │   ├── classifier.py      # LLM classification logic
│   │   │   ├── course_structure.py# Syllabus assembly
│   │   │   ├── library.py         # Content catalog mapping
│   │   │   ├── unified_hierarchy.py# Hierarchical CRUD & JSON schemas
│   │   │   ├── exceptions/        # App-wide exception handlers
│   │   │   └── logging/           # Structured console/file logs
│   │   │
│   │   ├── chunking/              # Chunker modules (hierarchical, validator)
│   │   ├── parser/                # PDF text extractors (Docling, PDFMiner)
│   │   ├── indexing/              # BM25 & FAISS builders and loaders
│   │   ├── query/                 # Query classification & expansion
│   │   ├── retrieval/             # Hybrid search, MMR filter, context filter
│   │   ├── reranker/              # Score-gap conditional LLM reranker
│   │   ├── rag/                   # LLM client & user multi-doc ask
│   │   ├── llm/                   # Trust scoring & citation builders
│   │   ├── generators/            # Prompt templates & quiz generators
│   │   ├── gamification/          # Leaderboard caches & levels
│   │   ├── personalization/       # User topic tracking & study planner
│   │   ├── evaluation/            # Grounding accuracy eval runner
│   │   ├── tasks/                 # Background workers & queue manager
│   │   │
│   │   ├── main.py                # FastAPI Application lifespan & router mounts
│   │   ├── config.py              # Configuration & Environment loading
│   │   ├── database.py            # SQLite ORM models & session creation
│   │   └── state.py               # Memory state maps (locks, caches)
│   │
│   └── frontend/                  # Single Page Application Frontend
│       ├── index.html             # Shell index page
│       ├── app.js                 # Global UI interactions and feature drivers
│       ├── styles.css             # Main styling system
│       ├── course.html            # Course Syllabus interface
│       ├── course.js              # Course Syllabus scripts
│       ├── course.css             # Course Syllabus styles
│       ├── search.html            # Search view page
│       ├── search.js              # Search logic script
│       ├── search.css             # Search page styling
│       ├── pdf-viewer.html        # Embedded PDF page viewer
│       ├── favicon.svg            # Site assets
│       └── app-icon.svg
│
├── storage/                       # Local File Storage Directory
│   ├── uploads/                   # Raw PDF uploads
│   ├── chunks/                    # Hierarchical JSON chunks
│   ├── faiss_index/               # Local dense index matrices
│   ├── library/                   # Unified topic trees
│   └── evaluation/                # Performance evaluation logs
│
└── learning_engine.db             # Local SQLite database
```

---

## 2. API Endpoints Map

### 🔒 Auth
*   `POST /api/register` -> `app.modules.auth.routes.register`
*   `POST /api/login` -> `app.modules.auth.routes.login`

### 📂 Ingestion & Ingest Pipeline
*   `POST /api/upload` -> `app.modules.upload_pipeline.routes.upload_document`
*   `POST /api/upload/multi` -> `app.modules.upload_pipeline.routes.upload_multiple_documents`
*   `GET /api/status/{doc_id}` -> `app.modules.upload_pipeline.routes.get_status`
*   `GET /api/status/user/{user_id}` -> `app.modules.upload_pipeline.routes.get_user_status`
*   `GET /api/documents/{user_id}` -> `app.modules.upload_pipeline.routes.list_documents`
*   `GET /api/pdf/{doc_id}` -> `app.modules.upload_pipeline.routes.serve_pdf`
*   `POST /api/retry/{doc_id}` -> `app.modules.upload_pipeline.routes.retry_document`

### 💬 Grounded Ask AI
*   `POST /api/ask` -> `app.modules.ask_ai.routes.ask_endpoint`
*   `POST /api/mentor` -> `app.modules.ask_ai.routes.mentor_endpoint`

### 📝 Quiz & Learning Content
*   `POST /api/quiz/start` -> `app.modules.quizzes.routes.start_quiz`
*   `POST /api/quiz/submit` -> `app.modules.quizzes.routes.submit_quiz`
*   `POST /api/generate` (Flashcards/Summaries) -> `app.modules.flashcards.routes.generate_content`

### 🔍 Search Engine
*   `POST /api/search` -> `app.modules.search_engine.routes.search`
*   `POST /api/search/user` -> `app.modules.search_engine.routes.search_user_scope`
*   `GET /api/search/suggest/{doc_id}` -> `app.modules.search_engine.routes.spell_suggest`
*   `GET /api/search/suggest/user/{user_id}` -> `app.modules.search_engine.routes.spell_suggest_user`
*   `GET /api/node_chunks/{doc_id}/{node_id}` -> `app.modules.search_engine.routes.get_chunks_for_node`

### 📊 Personalization & Weakness Detection
*   `GET /api/weakness/{user_id}` -> `app.modules.weaknesses.routes.get_weaknesses`

### 📚 Content Library
*   `GET /api/library` -> `app.modules.content_library.routes.get_library_stats`
*   `GET /api/library/hierarchy/{user_id}` -> `app.modules.content_library.routes.get_library_hierarchy`
*   `GET /api/library/{subject}` -> `app.modules.content_library.routes.get_subject_documents`
*   `POST /api/library/add` -> `app.modules.content_library.routes.add_to_library`
*   `POST /api/library/remove` -> `app.modules.content_library.routes.remove_from_library`
*   `POST /api/library/reclassify` -> `app.modules.content_library.routes.trigger_reclassification`

### 📖 Course System
*   `GET /api/course/{doc_id}/structure` -> `app.modules.courses.routes.get_structure`
*   `POST /api/course/action` -> `app.modules.courses.routes.perform_action`
*   `POST /api/course/chat` -> `app.modules.courses.routes.chat`

### 🏆 Gamification
*   `GET /api/leaderboard` -> `app.modules.gamification.routes.get_leaderboard`
*   `GET /api/score` -> `app.modules.gamification.routes.get_user_score`

### 📈 Evaluation & Diagnostics
*   `POST /api/evaluate/{doc_id}` -> `app.modules.evaluation.routes.run_eval`
*   `POST /api/compare/{doc_id}` -> `app.modules.evaluation.routes.run_comparison`
*   `POST /api/validate-reranker/{doc_id}` -> `app.modules.evaluation.routes.validate_reranker`
*   `POST /api/comparison-report/{doc_id}` -> `app.modules.evaluation.routes.run_comparison_report`
*   `GET /api/evaluation/report/{doc_id}` -> `app.modules.evaluation.routes.get_evaluation_report`
*   `GET /api/chunk-quality/{doc_id}` -> `app.modules.evaluation.routes.get_chunk_quality_metrics`
*   `GET /api/system/report/{doc_id}` -> `app.modules.evaluation.routes.get_system_report`
*   `POST /api/evaluate/stable/{doc_id}` -> `app.modules.evaluation.routes.run_stable_eval`
