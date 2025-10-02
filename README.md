# RAG-Based Recruitment System

A comprehensive, AI-powered recruitment system leveraging Retrieval-Augmented Generation (RAG) technology to intelligently match candidates with job positions. Built with FastAPI, React, and PostgreSQL.

## 🌟 Features

### Core Functionality
- **Intelligent Candidate Matching**: RAG-based semantic search to find the best candidates for job positions
- **Resume Processing**: Automated parsing and analysis of candidate resumes (PDF, DOCX)
- **Job Management**: Complete CRUD operations for job postings
- **Candidate Management**: Comprehensive candidate database with detailed profiles
- **Application Tracking**: End-to-end application workflow management
- **Interview Scheduling**: Built-in interview management system
- **User Authentication**: JWT-based secure authentication with role-based access control

### AI/ML Capabilities
- **Vector Embeddings**: Semantic understanding of resumes and job descriptions
- **LLM Integration**: Support for OpenAI GPT-4, Anthropic Claude, and local LLMs
- **RAG Pipeline**: Advanced retrieval and generation for intelligent recommendations
- **Semantic Search**: Find candidates based on meaning, not just keywords
- **Match Scoring**: Automated scoring of candidate-job fit

### User Roles
- **Admin**: Full system access and user management
- **Recruiter**: Manage jobs, candidates, and applications
- **Hiring Manager**: Review candidates and schedule interviews
- **Viewer**: Read-only access to system data

## 🏗️ Architecture

### Tech Stack

**Backend:**
- **Framework**: FastAPI 0.109.0 (Python 3.11+)
- **Database**: PostgreSQL with asyncpg
- **ORM**: SQLAlchemy 2.0 (async)
- **Authentication**: JWT tokens with bcrypt
- **AI/ML**:
  - LangChain for LLM orchestration
  - OpenAI/Anthropic/Ollama integration
  - ChromaDB/Qdrant for vector storage
- **Document Processing**: PyPDF2, python-docx
- **API Documentation**: Swagger/OpenAPI

**Frontend:**
- **Framework**: React 18.3 with TypeScript
- **Build Tool**: Vite 5.4
- **UI Library**: Material-UI (MUI) 5.16
- **Routing**: React Router 6.26
- **HTTP Client**: Axios
- **State Management**: React Hooks

**Database Schema:**
- 27+ tables covering candidates, jobs, applications, resumes, skills, interviews, and more
- Optimized indexes for fast queries
- Full JSONB support for flexible data storage

## 📋 Prerequisites

- **Python**: 3.11 or higher
- **Node.js**: 18.x or higher
- **PostgreSQL**: 14 or higher
- **Docker**: Optional, for containerized deployment

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd "Recruitement System"
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac

# Edit .env with your configuration
# Required: DATABASE_URL, SECRET_KEY, LLM provider settings
```

### 3. Database Setup

```bash
# Create PostgreSQL database
createdb recruitment_system

# Run migrations
alembic upgrade head

# Initialize default admin user
python -m app.scripts.init_db
```

### 4. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Create .env file (if needed)
# VITE_API_BASE_URL=http://localhost:8000
```

### 5. Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
.\venv\Scripts\activate  # Windows
source venv/bin/activate # Linux/Mac
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 6. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/v1/docs
- **Default Credentials**:
  - Username: `admin`
  - Password: `Admin123`

## 📁 Project Structure

```
Recruitement System/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── auth.py          # Authentication endpoints
│   │   │       ├── candidates.py    # Candidate CRUD
│   │   │       ├── jobs.py          # Job CRUD
│   │   │       ├── applications.py  # Application management
│   │   │       ├── resumes.py       # Resume processing
│   │   │       ├── search.py        # RAG search endpoints
│   │   │       └── matching.py      # Candidate-job matching
│   │   ├── models/
│   │   │   ├── user.py             # User & authentication
│   │   │   ├── candidate.py        # Candidate models
│   │   │   ├── job.py              # Job models
│   │   │   └── ...
│   │   ├── schemas/
│   │   │   ├── auth.py             # Pydantic schemas
│   │   │   ├── candidate.py
│   │   │   ├── job.py
│   │   │   └── ...
│   │   ├── services/
│   │   │   ├── auth_service.py     # Auth business logic
│   │   │   ├── generation/         # LLM integration
│   │   │   ├── embeddings/         # Vector embeddings
│   │   │   └── rag/                # RAG pipeline
│   │   ├── utils/
│   │   │   ├── security.py         # Password hashing
│   │   │   ├── jwt.py              # JWT utilities
│   │   │   └── ...
│   │   ├── dependencies/
│   │   │   └── auth.py             # FastAPI dependencies
│   │   ├── scripts/
│   │   │   └── init_db.py          # Database initialization
│   │   ├── config.py               # Configuration
│   │   ├── database.py             # Database connection
│   │   └── main.py                 # FastAPI application
│   ├── alembic/                    # Database migrations
│   ├── tests/                      # Backend tests
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── common/
│   │   │       └── Layout.tsx      # Main layout
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── LoginPage.tsx
│   │   │   ├── ProfilePage.tsx
│   │   │   ├── JobsPage.tsx        # Job management
│   │   │   ├── CandidatesPage.tsx  # Candidate management
│   │   │   └── ApplicationsPage.tsx
│   │   ├── services/
│   │   │   ├── api.ts              # Axios configuration
│   │   │   ├── authService.ts      # Authentication
│   │   │   ├── jobService.ts       # Job API calls
│   │   │   └── candidateService.ts # Candidate API calls
│   │   ├── App.tsx                 # Main app component
│   │   └── main.tsx                # Entry point
│   ├── package.json
│   └── .env
├── docs/                           # Documentation
│   ├── ARCHITECTURE.md
│   ├── PROCESS_FLOWS.md
│   └── API_REFERENCE.md
└── README.md                       # This file
```

## 🔐 Authentication

The system uses JWT-based authentication with the following flow:

1. User logs in with username/password
2. Server validates credentials and returns access + refresh tokens
3. Access token (15 min expiry) used for API requests
4. Refresh token (7 days expiry) used to get new access tokens
5. Tokens stored in localStorage on frontend

### API Authentication

All protected endpoints require the `Authorization` header:

```bash
Authorization: Bearer <access_token>
```

## 🗄️ Database Models

### Key Tables

**Users**: Authentication and authorization
- Roles: admin, recruiter, hiring_manager, viewer
- JWT token-based authentication
- Password hashing with bcrypt

**Candidates**: Candidate profiles
- Personal information
- Professional details (experience, skills, education)
- Resume storage and processing
- Status tracking (active, hired, blacklisted)

**Jobs**: Job postings
- Job description and requirements
- Salary range and employment details
- Status (draft, active, on_hold, closed)
- Required and preferred skills

**Applications**: Candidate-job applications
- Application status workflow
- Match scoring and explanations
- Interview scheduling
- Status history tracking

**Resumes**: Resume documents
- File storage (PDF, DOCX)
- Text extraction
- Chunking for RAG
- Vector embeddings

**Skills**: Candidate skills
- Skill name and category
- Proficiency levels
- Years of experience
- Verification status

## 🤖 AI/ML Features

### RAG Pipeline

1. **Document Ingestion**: Upload resume → Parse → Extract text
2. **Chunking**: Split into semantic chunks
3. **Embedding**: Generate vector embeddings
4. **Storage**: Store in vector database (ChromaDB/Qdrant)
5. **Retrieval**: Find relevant candidates for job
6. **Generation**: LLM generates match explanation

### LLM Integration

Supports multiple LLM providers:
- **OpenAI**: GPT-4, GPT-3.5-turbo
- **Anthropic**: Claude 3 (Opus, Sonnet, Haiku)
- **Ollama**: Local LLMs (Llama 2, Mistral, etc.)

Configure in `.env`:
```bash
LLM_PROVIDER=openai  # or anthropic, ollama
OPENAI_API_KEY=your-key
ANTHROPIC_API_KEY=your-key
OLLAMA_BASE_URL=http://localhost:11434
```

## 🔧 Configuration

### Backend Environment Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/recruitment_system

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# LLM Provider
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
DEFAULT_MODEL=gpt-4

# Vector Store
VECTOR_STORE_TYPE=chromadb
CHROMA_PERSIST_DIR=./chroma_data

# CORS
FRONTEND_URL=http://localhost:5173
```

### Frontend Environment Variables

```bash
VITE_API_BASE_URL=http://localhost:8000
```

## 📊 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user
- `PUT /api/v1/auth/me` - Update profile
- `POST /api/v1/auth/change-password` - Change password

### Jobs
- `GET /api/v1/jobs` - List jobs (paginated, filtered)
- `POST /api/v1/jobs` - Create job
- `GET /api/v1/jobs/{id}` - Get job details
- `PUT /api/v1/jobs/{id}` - Update job
- `DELETE /api/v1/jobs/{id}` - Delete job
- `POST /api/v1/jobs/{id}/activate` - Activate job
- `POST /api/v1/jobs/{id}/close` - Close job

### Candidates
- `GET /api/v1/candidates` - List candidates
- `POST /api/v1/candidates` - Create candidate
- `GET /api/v1/candidates/{id}` - Get candidate
- `PUT /api/v1/candidates/{id}` - Update candidate
- `DELETE /api/v1/candidates/{id}` - Delete candidate
- `POST /api/v1/candidates/{id}/resumes` - Upload resume

### RAG & Search
- `POST /api/v1/search/candidates` - Semantic candidate search
- `POST /api/v1/jobs/{id}/match` - Find matching candidates
- `GET /api/v1/jobs/{id}/recommendations` - Get recommendations

Full API documentation available at: http://localhost:8000/api/v1/docs

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm run test
```

## 🚢 Deployment

### Docker Deployment

```bash
# Build images
docker-compose build

# Run services
docker-compose up -d

# View logs
docker-compose logs -f
```

### Manual Deployment

**Backend:**
```bash
# Use Gunicorn with Uvicorn workers
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

**Frontend:**
```bash
# Build production bundle
npm run build

# Serve with nginx or any static server
```

## 🔍 Troubleshooting

### Common Issues

**Database Connection Error:**
- Check PostgreSQL is running
- Verify DATABASE_URL in .env
- Ensure database exists

**LLM API Errors:**
- Verify API keys in .env
- Check LLM_PROVIDER setting
- Ensure sufficient API credits

**Frontend Can't Connect to Backend:**
- Check VITE_API_BASE_URL in frontend/.env
- Verify CORS settings in backend
- Ensure backend is running

**Migration Errors:**
```bash
# Reset database
alembic downgrade base
alembic upgrade head
```

## 📈 Performance Optimization

- Database indexes on frequently queried fields
- Connection pooling for database
- Async/await throughout backend
- React component memoization
- Lazy loading for large lists
- Efficient vector search algorithms

## 🔒 Security Features

- Password hashing with bcrypt (cost factor 12)
- JWT token authentication
- CORS protection
- SQL injection prevention (ORM)
- XSS protection
- Rate limiting (recommended for production)
- Input validation with Pydantic

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Author

- Project Idea & Development Team - Shekar Kaki
- https://urbanschool369.com
- https://indiantalent.net

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- LangChain for LLM orchestration
- Material-UI for the component library
- OpenAI/Anthropic for AI capabilities

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check documentation in `/docs` folder
- You can reach urbanschool369@gmail.com

## 🗺️ Roadmap Future developement

- [ ] Email notifications for applications
- [ ] Advanced analytics dashboard
- [ ] Mobile app (React Native)
- [ ] Integration with LinkedIn API
- [ ] Calendar integration for interviews
- [ ] Advanced reporting features
- [ ] Multi-language support
- [ ] Dark mode theme
- [ ] Export to Excel/CSV
- [ ] Bulk operations

## 📊 System Requirements

**Development:**
- CPU: 2+ cores
- RAM: 4GB minimum
- Disk: 10GB free space

**Production:**
- CPU: 4+ cores
- RAM: 8GB minimum
- Disk: 50GB+ (depends on resume storage)
- PostgreSQL: 14+
- Redis: 6+ (for caching, optional)

---

**Built with ❤️ using FastAPI and React**
