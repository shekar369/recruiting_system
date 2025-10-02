# System Architecture

## Overview

The RAG-Based Recruitment System follows a modern three-tier architecture with microservices principles, combining traditional CRUD operations with advanced AI/ML capabilities for intelligent candidate matching.

## High-Level Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                           Client Layer                                   │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    React Frontend (SPA)                           │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐         │  │
│  │  │Dashboard │  │   Jobs   │  │Candidates│  │  Profile │         │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘         │  │
│  │                                                                    │  │
│  │  Material-UI Components | React Router | Axios HTTP Client       │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTPS/REST API
                                    │ JWT Authentication
                                    ↓
┌────────────────────────────────────────────────────────────────────────┐
│                      Application Layer (Backend)                        │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                       FastAPI Server                              │  │
│  │  ┌─────────────────────────────────────────────────────────────┐ │  │
│  │  │                    API Endpoints (v1)                        │ │  │
│  │  │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌─────────┐ │ │  │
│  │  │  │ Auth │ │ Jobs │ │Candid│ │Resume│ │Search│ │ Matching│ │ │  │
│  │  │  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └─────────┘ │ │  │
│  │  └─────────────────────────────────────────────────────────────┘ │  │
│  │  ┌─────────────────────────────────────────────────────────────┐ │  │
│  │  │                   Business Logic Layer                       │ │  │
│  │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │ │  │
│  │  │  │Auth Service  │  │CRUD Services │  │   RAG Service    │  │ │  │
│  │  │  └──────────────┘  └──────────────┘  └──────────────────┘  │ │  │
│  │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │ │  │
│  │  │  │LLM Generator │  │  Embeddings  │  │Document Processor│  │ │  │
│  │  │  └──────────────┘  └──────────────┘  └──────────────────┘  │ │  │
│  │  └─────────────────────────────────────────────────────────────┘ │  │
│  │  ┌─────────────────────────────────────────────────────────────┐ │  │
│  │  │                    Data Access Layer                         │ │  │
│  │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │ │  │
│  │  │  │SQLAlchemy ORM│  │  Pydantic    │  │  Dependencies    │  │ │  │
│  │  │  └──────────────┘  └──────────────┘  └──────────────────┘  │ │  │
│  │  └─────────────────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Database Connections
                                    ↓
┌────────────────────────────────────────────────────────────────────────┐
│                          Data Layer                                     │
│  ┌────────────────────┐  ┌────────────────────┐  ┌─────────────────┐  │
│  │   PostgreSQL DB    │  │  Vector Database   │  │  File Storage   │  │
│  │                    │  │  (ChromaDB/Qdrant) │  │  (Local/S3)     │  │
│  │  ┌──────────────┐  │  │                    │  │                 │  │
│  │  │ 27+ Tables   │  │  │  ┌──────────────┐  │  │  ┌───────────┐ │  │
│  │  │              │  │  │  │  Embeddings  │  │  │  │  Resumes  │ │  │
│  │  │ Candidates   │  │  │  │   Vectors    │  │  │  │   PDFs    │ │  │
│  │  │ Jobs         │  │  │  │  Metadata    │  │  │  │   DOCX    │ │  │
│  │  │ Applications │  │  │  └──────────────┘  │  │  └───────────┘ │  │
│  │  │ Resumes      │  │  │                    │  │                 │  │
│  │  │ Skills       │  │  │                    │  │                 │  │
│  │  │ Users        │  │  │                    │  │                 │  │
│  │  └──────────────┘  │  │                    │  │                 │  │
│  └────────────────────┘  └────────────────────┘  └─────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ External APIs
                                    ↓
┌────────────────────────────────────────────────────────────────────────┐
│                     External Services Layer                             │
│  ┌────────────────────┐  ┌────────────────────┐  ┌─────────────────┐  │
│  │   LLM Providers    │  │  Email Service     │  │  Cloud Storage  │  │
│  │                    │  │                    │  │                 │  │
│  │  ┌──────────────┐  │  │  ┌──────────────┐  │  │  ┌───────────┐ │  │
│  │  │   OpenAI     │  │  │  │    SMTP      │  │  │  │    S3     │ │  │
│  │  │  Anthropic   │  │  │  │  SendGrid    │  │  │  │   Azure   │ │  │
│  │  │   Ollama     │  │  │  └──────────────┘  │  │  └───────────┘ │  │
│  │  └──────────────┘  │  │                    │  │                 │  │
│  └────────────────────┘  └────────────────────┘  └─────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

## Component Architecture

### Frontend Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    React Application                             │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    App.tsx (Root)                        │    │
│  │  ┌─────────────────────────────────────────────────┐   │    │
│  │  │        React Router Configuration               │   │    │
│  │  │  ┌────────────┐  ┌────────────┐  ┌───────────┐ │   │    │
│  │  │  │Public Routes│  │Auth Routes │  │Protected  │ │   │    │
│  │  │  └────────────┘  └────────────┘  └───────────┘ │   │    │
│  │  └─────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                      Pages                               │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌────────────────┐  │    │
│  │  │  Dashboard  │  │  JobsPage   │  │ CandidatesPage │  │    │
│  │  │  LoginPage  │  │ProfilePage  │  │ApplicationsPage│  │    │
│  │  └─────────────┘  └─────────────┘  └────────────────┘  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   Components                             │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌────────────────┐  │    │
│  │  │   Layout    │  │   Dialogs   │  │     Forms      │  │    │
│  │  │   Tables    │  │   Cards     │  │    Buttons     │  │    │
│  │  └─────────────┘  └─────────────┘  └────────────────┘  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    Services Layer                        │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌────────────────┐  │    │
│  │  │ authService │  │ jobService  │  │candidateService│  │    │
│  │  │     api     │  │appService   │  │  searchService │  │    │
│  │  └─────────────┘  └─────────────┘  └────────────────┘  │    │
│  │                    (Axios HTTP Client)                   │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### Backend Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   FastAPI Application                            │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │               main.py (Application Factory)              │    │
│  │  - CORS Middleware                                        │    │
│  │  - Authentication Middleware                              │    │
│  │  - Error Handlers                                         │    │
│  │  - Router Registration                                    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    API Layer (v1)                        │    │
│  │  ┌────────────┐  ┌────────────┐  ┌──────────────────┐  │    │
│  │  │  auth.py   │  │  jobs.py   │  │  candidates.py   │  │    │
│  │  │            │  │            │  │                  │  │    │
│  │  │ - login    │  │ - list     │  │ - list           │  │    │
│  │  │ - register │  │ - create   │  │ - create         │  │    │
│  │  │ - refresh  │  │ - update   │  │ - update         │  │    │
│  │  │ - me       │  │ - delete   │  │ - delete         │  │    │
│  │  └────────────┘  └────────────┘  └──────────────────┘  │    │
│  │  ┌────────────┐  ┌────────────┐  ┌──────────────────┐  │    │
│  │  │resumes.py  │  │search.py   │  │  matching.py     │  │    │
│  │  │            │  │            │  │                  │  │    │
│  │  │ - upload   │  │ - semantic │  │ - find_matches   │  │    │
│  │  │ - process  │  │ - hybrid   │  │ - get_score      │  │    │
│  │  └────────────┘  └────────────┘  └──────────────────┘  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   Services Layer                         │    │
│  │  ┌─────────────────────┐  ┌────────────────────────┐    │    │
│  │  │  auth_service.py    │  │  CRUD Services         │    │    │
│  │  │  - authenticate     │  │  - create/read/update  │    │    │
│  │  │  - create_tokens    │  │  - delete operations   │    │    │
│  │  │  - verify_token     │  │                        │    │    │
│  │  └─────────────────────┘  └────────────────────────┘    │    │
│  │                                                           │    │
│  │  ┌─────────────────────┐  ┌────────────────────────┐    │    │
│  │  │  RAG Services       │  │  AI/ML Services        │    │    │
│  │  │  - retrieval        │  │  - embeddings          │    │    │
│  │  │  - generation       │  │  - llm_generation      │    │    │
│  │  │  - vector_search    │  │  - document_parsing    │    │    │
│  │  └─────────────────────┘  └────────────────────────┘    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    Models Layer                          │    │
│  │  ┌────────────┐  ┌────────────┐  ┌──────────────────┐  │    │
│  │  │  user.py   │  │  job.py    │  │  candidate.py    │  │    │
│  │  │ resume.py  │  │  skill.py  │  │  application.py  │  │    │
│  │  └────────────┘  └────────────┘  └──────────────────┘  │    │
│  │        (SQLAlchemy ORM Models - 27+ tables)             │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   Schemas Layer                          │    │
│  │  ┌────────────┐  ┌────────────┐  ┌──────────────────┐  │    │
│  │  │  auth.py   │  │  job.py    │  │  candidate.py    │  │    │
│  │  └────────────┘  └────────────┘  └──────────────────┘  │    │
│  │          (Pydantic Models for Validation)               │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## Database Schema

### Core Tables Relationships

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│    Users     │         │     Jobs     │         │  Candidates  │
│──────────────│         │──────────────│         │──────────────│
│ id (PK)      │         │ id (PK)      │         │ id (PK)      │
│ username     │         │ title        │         │ first_name   │
│ email        │         │ description  │         │ last_name    │
│ password_hash│         │ department   │         │ email        │
│ role         │         │ location     │         │ phone        │
│ is_active    │         │ salary_range │         │ location     │
│ created_at   │         │ status       │         │ experience   │
│ last_login   │         │ created_at   │         │ status       │
└──────────────┘         └──────────────┘         └──────────────┘
       │                        │                         │
       │                        │                         │
       │                        └────────┬────────────────┘
       │                                 │
       │                                 ↓
       │                    ┌─────────────────────────┐
       │                    │     Applications        │
       │                    │─────────────────────────│
       │                    │ id (PK)                 │
       │                    │ job_id (FK)             │
       │                    │ candidate_id (FK)       │
       │                    │ resume_id (FK)          │
       │                    │ status                  │
       │                    │ match_score             │
       │                    │ applied_at              │
       │                    │ reviewed_at             │
       │                    └─────────────────────────┘
       │                                 │
       │                                 │
       │                                 ↓
       │                    ┌─────────────────────────┐
       │                    │      Interviews         │
       │                    │─────────────────────────│
       │                    │ id (PK)                 │
       │                    │ application_id (FK)     │
       │                    │ scheduled_at            │
       │                    │ interviewer             │
       │                    │ feedback                │
       │                    │ rating                  │
       │                    └─────────────────────────┘
       │
       └─────────────────►┌─────────────────────────┐
                          │   Candidate_Resumes     │
                          │─────────────────────────│
                          │ id (PK)                 │
                          │ candidate_id (FK)       │
                          │ file_path               │
                          │ raw_text                │
                          │ is_processed            │
                          │ is_embedded             │
                          └─────────────────────────┘
                                     │
                                     │
                                     ↓
                          ┌─────────────────────────┐
                          │    Resume_Chunks        │
                          │─────────────────────────│
                          │ id (PK)                 │
                          │ resume_id (FK)          │
                          │ content                 │
                          │ chunk_index             │
                          │ embedding_id            │
                          └─────────────────────────┘
```

### Additional Tables

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│Candidate     │    │Candidate     │    │Candidate     │
│Skills        │    │Experience    │    │Education     │
└──────────────┘    └──────────────┘    └──────────────┘

┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│Candidate     │    │Application   │    │Job           │
│Certifications│    │Status_History│    │Recommendations│
└──────────────┘    └──────────────┘    └──────────────┘
```

## RAG Pipeline Architecture

```
┌────────────────────────────────────────────────────────────┐
│                  RAG Pipeline Flow                          │
│                                                              │
│  ┌──────────────┐                                          │
│  │ 1. Document  │                                          │
│  │   Ingestion  │                                          │
│  └──────┬───────┘                                          │
│         │                                                   │
│         ↓                                                   │
│  ┌──────────────┐      ┌─────────────┐                    │
│  │ 2. Text      │───┬─→│ PDF Parser  │                    │
│  │  Extraction  │   │  └─────────────┘                    │
│  └──────┬───────┘   │  ┌─────────────┐                    │
│         │           └─→│ DOCX Parser │                    │
│         ↓              └─────────────┘                    │
│  ┌──────────────┐                                          │
│  │ 3. Text      │                                          │
│  │   Cleaning   │                                          │
│  └──────┬───────┘                                          │
│         │                                                   │
│         ↓                                                   │
│  ┌──────────────┐      ┌──────────────────────┐           │
│  │ 4. Chunking  │─────→│ Semantic Chunking    │           │
│  │              │      │ (512 tokens/chunk)   │           │
│  └──────┬───────┘      └──────────────────────┘           │
│         │                                                   │
│         ↓                                                   │
│  ┌──────────────┐      ┌──────────────────────┐           │
│  │ 5. Embedding │─────→│ Sentence Transformers│           │
│  │              │      │ (384/768 dimensions) │           │
│  └──────┬───────┘      └──────────────────────┘           │
│         │                                                   │
│         ↓                                                   │
│  ┌──────────────┐      ┌──────────────────────┐           │
│  │ 6. Storage   │─────→│   Vector Database    │           │
│  │              │      │  (ChromaDB/Qdrant)   │           │
│  └──────────────┘      └──────────────────────┘           │
│                                                              │
│  ──────────────────── Retrieval Phase ─────────────────── │
│                                                              │
│  ┌──────────────┐                                          │
│  │ 7. Query     │ ← User/System Query                      │
│  │  Processing  │                                          │
│  └──────┬───────┘                                          │
│         │                                                   │
│         ↓                                                   │
│  ┌──────────────┐      ┌──────────────────────┐           │
│  │ 8. Vector    │─────→│  Similarity Search   │           │
│  │   Search     │      │  (Cosine/Euclidean)  │           │
│  └──────┬───────┘      └──────────────────────┘           │
│         │                                                   │
│         ↓                                                   │
│  ┌──────────────┐      ┌──────────────────────┐           │
│  │ 9. Re-ranking│─────→│  Score & Filter      │           │
│  │              │      │   Top-K Results      │           │
│  └──────┬───────┘      └──────────────────────┘           │
│         │                                                   │
│         ↓                                                   │
│  ┌──────────────┐      ┌──────────────────────┐           │
│  │10. Generation│─────→│   LLM Processing     │           │
│  │              │      │  (GPT-4/Claude/Llama)│           │
│  └──────┬───────┘      └──────────────────────┘           │
│         │                                                   │
│         ↓                                                   │
│  ┌──────────────┐                                          │
│  │11. Response  │ → Structured Output                      │
│  │  Formatting  │                                          │
│  └──────────────┘                                          │
└────────────────────────────────────────────────────────────┘
```

## Security Architecture

```
┌────────────────────────────────────────────────────────────┐
│                   Security Layers                           │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Frontend Security                       │   │
│  │  - Token storage in localStorage                    │   │
│  │  - Auto token refresh                               │   │
│  │  - Protected routes with auth guards                │   │
│  │  - XSS protection (React escaping)                  │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                  │
│                           ↓                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Network Security                        │   │
│  │  - HTTPS/TLS encryption                             │   │
│  │  - CORS policy enforcement                          │   │
│  │  - Rate limiting (recommended)                      │   │
│  │  - API versioning                                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                  │
│                           ↓                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           Application Security                       │   │
│  │  - JWT token validation                             │   │
│  │  - Role-based access control (RBAC)                 │   │
│  │  - Request validation (Pydantic)                    │   │
│  │  - SQL injection prevention (ORM)                   │   │
│  │  - Input sanitization                               │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                  │
│                           ↓                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Data Security                           │   │
│  │  - Password hashing (bcrypt, cost=12)              │   │
│  │  - Encrypted database connections                   │   │
│  │  - Secure file storage                              │   │
│  │  - Audit logging                                    │   │
│  └─────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────┘
```

## Deployment Architecture

### Development Environment
```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Frontend   │    │   Backend    │    │  PostgreSQL  │
│   (Vite)     │    │  (Uvicorn)   │    │   (Local)    │
│ :5173        │───→│  :8000       │───→│  :5432       │
└──────────────┘    └──────────────┘    └──────────────┘
```

### Production Environment (Recommended)
```
┌─────────────────────────────────────────────────────────────┐
│                        Load Balancer                         │
│                       (Nginx/ALB)                            │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ↓                         ↓
┌──────────────┐          ┌──────────────┐
│   Frontend   │          │   Backend    │
│    (Nginx)   │          │  (Gunicorn)  │
│   Static     │          │   Workers    │
│   Files      │          │   :8000      │
└──────────────┘          └──────┬───────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ↓                         ↓
            ┌──────────────┐          ┌──────────────┐
            │  PostgreSQL  │          │   Vector DB  │
            │   (RDS)      │          │  (ChromaDB)  │
            │   :5432      │          │              │
            └──────────────┘          └──────────────┘
```

## Technology Stack Details

### Backend Technologies
- **FastAPI 0.109.0**: Modern async web framework
- **SQLAlchemy 2.0**: Async ORM for database operations
- **Pydantic 2.5**: Data validation and serialization
- **Asyncpg**: Async PostgreSQL driver
- **Bcrypt**: Password hashing
- **PyJWT**: JWT token handling
- **LangChain**: LLM orchestration
- **ChromaDB/Qdrant**: Vector storage
- **Alembic**: Database migrations

### Frontend Technologies
- **React 18.3**: UI framework
- **TypeScript**: Type-safe JavaScript
- **Vite 5.4**: Build tool and dev server
- **Material-UI 5.16**: Component library
- **React Router 6.26**: Client-side routing
- **Axios**: HTTP client
- **React Hooks**: State management

### Infrastructure
- **PostgreSQL 14+**: Relational database
- **Docker**: Containerization
- **Nginx**: Reverse proxy and static files
- **Gunicorn**: WSGI HTTP server
- **Redis (Optional)**: Caching and sessions

## Scalability Considerations

1. **Horizontal Scaling**: Multiple backend instances behind load balancer
2. **Database Read Replicas**: Separate read and write operations
3. **Caching Layer**: Redis for frequently accessed data
4. **CDN**: Static asset delivery
5. **Async Processing**: Background jobs for heavy operations
6. **Vector Database Sharding**: Distribute embeddings across nodes
7. **API Rate Limiting**: Protect against abuse
8. **Monitoring**: Application performance monitoring (APM)

## Performance Optimizations

- Database indexes on frequently queried fields
- Connection pooling
- Lazy loading of relationships
- Query result caching
- Vector search optimizations
- Batch processing for embeddings
- Async/await throughout backend
- Code splitting in frontend
- Image optimization
- Gzip compression

---

**Last Updated**: 2025-10-02
