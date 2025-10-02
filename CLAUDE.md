# RAG Recruiting System - Quick Reference Card

## 🚀 Essential Commands

### Starting Services
```bash
# Start PostgreSQL (if not running)
docker run -d --name postgres -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=recruiting_db -p 5432:5432 postgres:15

# Start all services with Docker Compose
docker-compose up -d

# Start backend only
cd backend
uvicorn app.main:app --reload

# Start frontend only
cd frontend
npm run dev

# Start Celery worker
cd backend
celery -A app.workers.celery_app worker --loglevel=info
```

### Development Commands
```bash
# Install backend dependencies
cd backend && pip install -r requirements.txt

# Install frontend dependencies
cd frontend && npm install

# Run database migrations
cd backend && alembic upgrade head

# Create new migration
cd backend && alembic revision --autogenerate -m "description"

# Run tests
cd backend && pytest
cd frontend && npm test

# Check code quality
cd backend && black . && flake8
cd frontend && npm run lint
```

### Useful Checks
```bash
# Check what's running
docker-compose ps
docker ps
lsof -i :8000  # Backend
lsof -i :5173  # Frontend
lsof -i :5432  # PostgreSQL

# View logs
docker-compose logs -f backend
docker-compose logs -f celery_worker

# Test database connection
psql -h localhost -U user -d recruiting_db

# Test Redis connection
docker exec -it <redis-container> redis-cli ping
```

---

## 📍 Important URLs

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:5173 | React UI |
| **Backend API** | http://localhost:8000 | FastAPI endpoints |
| **API Docs** | http://localhost:8000/docs | Swagger UI |
| **API Redoc** | http://localhost:8000/redoc | ReDoc UI |
| **PostgreSQL** | localhost:5432 | Database |
| **Redis** | localhost:6379 | Cache & Celery |

---

## 🗺️ 25-Session Development Roadmap

### 📦 PHASE 1: Foundation (Sessions 1-4)
**Goal**: Basic project setup with CRUD operations

- **Session 1**: Project structure, Docker, configs ✅ (START HERE)
- **Session 2**: FastAPI + React initialization ✅
- **Session 3**: Database models & migrations
- **Session 4**: Basic CRUD APIs for candidates & jobs

**Milestone**: Can create/read/update/delete candidates and jobs

---

### 📄 PHASE 2: Document Processing (Sessions 5-7)
**Goal**: Resume upload, extraction, and chunking

- **Session 5**: File upload & local storage
- **Session 6**: Document extraction (PDF/Word)
- **Session 7**: Semantic chunking with LangChain

**Milestone**: Can upload resumes and extract structured data

---

### 🧠 PHASE 3: Embeddings & Vectors (Sessions 8-10)
**Goal**: Vector database setup with FAISS

- **Session 8**: Sentence Transformers embedding service
- **Session 9**: FAISS vector store integration
- **Session 10**: Batch processing with Celery

**Milestone**: Can generate embeddings for all resumes

---

### 🔍 PHASE 4: Search & Matching (Sessions 11-13)
**Goal**: Intelligent candidate-job matching

- **Session 11**: Hybrid search (PostgreSQL + FAISS)
- **Session 12**: Reranking service
- **Session 13**: Job-candidate matching engine

**Milestone**: Can match candidates to jobs with high accuracy

---

### 🤖 PHASE 5: LLM Generation (Session 14)
**Goal**: Add AI-powered features

- **Session 14**: Generation service (Ollama/OpenAI/Claude)

**Milestone**: AI summaries and recommendations working

---

### 🔗 PHASE 6: External Integrations (Sessions 15-17)
**Goal**: Sync data from external platforms

- **Session 15**: LinkedIn integration
- **Session 16**: GitHub integration
- **Session 17**: Medium, YouTube, StackOverflow

**Milestone**: Rich candidate profiles from multiple sources

---

### 🔄 PHASE 7: Deduplication (Session 18)
**Goal**: Detect and merge duplicate candidates

- **Session 18**: Fuzzy matching & merge logic

**Milestone**: No duplicate candidates in system

---

### 📋 PHASE 8: Applications (Sessions 19-20)
**Goal**: Complete application workflow

- **Session 19**: Application management & tracking
- **Session 20**: Interview scheduling

**Milestone**: Full recruitment pipeline working

---

### 📊 PHASE 9: Analytics & Polish (Sessions 21-22)
**Goal**: Dashboard and UI improvements

- **Session 21**: Analytics dashboard
- **Session 22**: UI/UX polish

**Milestone**: Production-ready user interface

---

### ✅ PHASE 10: Testing & Deployment (Sessions 23-25)
**Goal**: Production readiness

- **Session 23**: Backend tests
- **Session 24**: Frontend tests
- **Session 25**: Deployment preparation

**Milestone**: Tested, documented, ready to deploy

---

## 🎯 Current Focus Tracker

```
┌─────────────────────────────────────────┐
│  CURRENT PHASE: 1 - Foundation          │
│  CURRENT SESSION: 1 - Project Setup     │
│  PROGRESS: ░░░░░░░░░░░░░░░░░░░░ 0%      │
│  NEXT: Initialize project structure     │
└─────────────────────────────────────────┘
```

Update this after each session!

---

## 📝 Session Template

Use this for each Claude Code session:

```
SESSION [NUMBER]: [TITLE]
Date: [Today's date]
Duration: ~60 min

CONTEXT:
- Previous session completed: [Session X]
- Current status: [Brief description]
- Files modified: [List key files]

GOAL: [Specific goal for this session]

PROMPT TO CLAUDE CODE:
[Paste the session prompt here]

RESULTS:
✅ Completed: [What was done]
⚠️ Issues: [Any problems encountered]
📝 Notes: [Important learnings]

NEXT SESSION: [Session X+1]
```

---

## 🔑 Key File Locations

### Backend
```
backend/
├── app/main.py              # FastAPI entry point
├── app/config.py            # Configuration
├── app/database.py          # DB connection
├── app/models/              # SQLAlchemy models
├── app/schemas/             # Pydantic schemas
├── app/api/v1/              # API endpoints
├── app/services/            # Business logic
├── uploads/resumes/         # Uploaded files
└── data/faiss_index/        # Vector index
```

### Frontend
```
frontend/
├── src/App.tsx              # Main app component
├── src/main.tsx             # Entry point
├── src/services/api.ts      # API client
├── src/store/               # Redux store
├── src/components/          # React components
└── src/pages/               # Page components
```

---

## 🐛 Quick Debugging

### Backend Issues
```python
# Add debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Test database
from app.database import engine
engine.connect()

# Test import
from app.models import candidate
```

### Frontend Issues
```typescript
// Check API connection
console.log(import.meta.env.VITE_API_BASE_URL)

// Test API call
import { api } from './services/api'
api.get('/').then(console.log)
```

### FAISS Issues
```python
# Check FAISS installation
import faiss
print(faiss.__version__)

# Test index creation
import numpy as np
index = faiss.IndexFlatL2(384)
vectors = np.random.random((10, 384)).astype('float32')
index.add(vectors)
print(f"Index has {index.ntotal} vectors")
```

---

## 📊 Success Metrics

Track these after each phase:

| Phase | Metric | Target |
|-------|--------|--------|
| 1 | APIs working | 100% CRUD |
| 2 | Resumes parsed | 90%+ accuracy |
| 3 | Embeddings generated | <30s per resume |
| 4 | Search relevance | 85%+ match quality |
| 5 | LLM responses | <5s response time |
| 6 | Integration sync | 5+ platforms |
| 7 | Duplicate detection | 95%+ accuracy |
| 8 | Application tracking | Full workflow |
| 9 | UI responsiveness | <500ms interactions |
| 10 | Test coverage | >80% |

---

## 💾 Git Commit Messages

Use conventional commits:

```bash
# After Session 1
git commit -m "feat: initialize project structure"

# After Session 3
git commit -m "feat: add database models and migrations"

# After Session 5
git commit -m "feat: implement file upload with local storage"

# Bug fix
git commit -m "fix: resolve FAISS index persistence issue"

# Documentation
git commit -m "docs: update API documentation"
```

---

## 🆘 Need Help?

### During a Session
```
Claude Code, I'm stuck on [issue].

Current error: [paste error]
What I tried: [describe attempts]
Context: [relevant code/config]

Please help me:
1. Understand the root cause
2. Fix the issue
3. Prevent it in the future
```

### Between Sessions
```
Claude Code, let's review what we built in Session [X].

Please:
1. Summarize what was accomplished
2. Identify any issues or technical debt
3. Suggest improvements
4. Prepare for Session [X+1]
```

---

## 🎓 Learning Resources

### FastAPI
- Docs: https://fastapi.tiangolo.com
- Tutorial: https://fastapi.tiangolo.com/tutorial/

### React + TypeScript
- React: https://react.dev
- TypeScript: https://www.typescriptlang.org/docs/

### RAG & Embeddings
- LangChain: https://python.langchain.com/docs/get_started/introduction
- Sentence Transformers: https://www.sbert.net
- FAISS: https://github.com/facebookresearch/faiss

### PostgreSQL
- Docs: https://www.postgresql.org/docs/
- SQLAlchemy: https://docs.sqlalchemy.org/

---

## ⏱️ Estimated Timeline

| Phase | Sessions | Duration | Calendar |
|-------|----------|----------|----------|
| Phase 1 | 1-4 | 4 hours | Day 1 |
| Phase 2 | 5-7 | 3 hours | Day 2 |
| Phase 3 | 8-10 | 4 hours | Day 3-4 |
| Phase 4 | 11-13 | 4 hours | Day 5-6 |
| Phase 5 | 14 | 1 hour | Day 7 |
| Phase 6 | 15-17 | 4 hours | Day 8-9 |
| Phase 7 | 18 | 1.5 hours | Day 10 |
| Phase 8 | 19-20 | 3 hours | Day 11 |
| Phase 9 | 21-22 | 3 hours | Day 12 |
| Phase 10 | 23-25 | 4 hours | Day 13-14 |
| **TOTAL** | **25** | **~32 hours** | **~2 weeks** |

*Working 2-3 hours per day*

---

## 🎯 First 3 Sessions - Quick Start

### RIGHT NOW: Session 1
**Time**: 60 minutes  
**Goal**: Project structure + config  
**Status**: Ready to start!  
**Action**: Open Claude Code, paste Session 1A prompt

### NEXT: Session 2
**Time**: 45 minutes  
**Goal**: FastAPI + React running  
**Prereq**: Session 1 complete  
**Action**: Use Session 2A prompt

### THEN: Session 3
**Time**: 60 minutes  
**Goal**: Database models  
**Prereq**: Backend running  
**Action**: Start with candidate models

---

## ✅ Ready Checklist

Before starting each session:

- [ ] Previous session completed successfully
- [ ] All services running (backend/frontend/DB)
- [ ] No git conflicts
- [ ] Environment variables set
- [ ] Claude Code open
- [ ] Specification document available
- [ ] Coffee ready ☕

---

## 🎉 Milestone Celebrations

- ✅ Session 4: First working CRUD - Test with real data!
- ✅ Session 7: First resume parsed - Check extraction quality
- ✅ Session 10: First embeddings - Run similarity search
- ✅ Session 13: First job match - See the magic happen!
- ✅ Session 18: Duplicates detected - Data quality improved
- ✅ Session 25: Production ready - Deploy and celebrate! 🚀

---

**Print this card or keep it handy during development!**

Last Updated: [Current Date]
Project: RAG Recruiting System
Version: 1.0
