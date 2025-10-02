# Process Flow Diagrams

This document describes the key business processes and workflows in the RAG-Based Recruitment System.

## 1. User Authentication Flow

### Login Process

```
┌─────────┐         ┌─────────┐         ┌─────────┐         ┌─────────┐
│  User   │         │Frontend │         │ Backend │         │Database │
└────┬────┘         └────┬────┘         └────┬────┘         └────┬────┘
     │                   │                   │                   │
     │ Enter credentials │                   │                   │
     ├──────────────────►│                   │                   │
     │                   │ POST /auth/login  │                   │
     │                   ├──────────────────►│                   │
     │                   │                   │ Query user        │
     │                   │                   ├──────────────────►│
     │                   │                   │                   │
     │                   │                   │◄──────────────────┤
     │                   │                   │ User data         │
     │                   │                   │                   │
     │                   │                   │ Verify password   │
     │                   │                   │ (bcrypt)          │
     │                   │                   │                   │
     │                   │                   │ Generate tokens   │
     │                   │                   │ (JWT)             │
     │                   │                   │                   │
     │                   │◄──────────────────┤                   │
     │                   │ Access + Refresh  │                   │
     │                   │ tokens            │                   │
     │◄──────────────────┤                   │                   │
     │ Redirect to       │                   │                   │
     │ Dashboard         │                   │                   │
     │                   │                   │                   │
```

### Token Refresh Flow

```
┌─────────┐         ┌─────────┐         ┌─────────┐
│Frontend │         │ Backend │         │Database │
└────┬────┘         └────┬────┘         └────┬────┘
     │                   │                   │
     │ Access token      │                   │
     │ expires (15 min)  │                   │
     │                   │                   │
     │ POST /auth/refresh│                   │
     ├──────────────────►│                   │
     │ (refresh token)   │                   │
     │                   │ Verify refresh    │
     │                   │ token             │
     │                   │                   │
     │                   │ Query user        │
     │                   ├──────────────────►│
     │                   │◄──────────────────┤
     │                   │                   │
     │                   │ Generate new      │
     │                   │ tokens            │
     │                   │                   │
     │◄──────────────────┤                   │
     │ New access token  │                   │
     │                   │                   │
```

## 2. Job Management Flow

### Create Job Posting

```
┌──────────┐      ┌─────────┐      ┌─────────┐      ┌─────────┐
│Recruiter │      │Frontend │      │ Backend │      │Database │
└────┬─────┘      └────┬────┘      └────┬────┘      └────┬────┘
     │                 │                │                │
     │ Click "Post     │                │                │
     │ New Job"        │                │                │
     ├────────────────►│                │                │
     │                 │                │                │
     │                 │ Display form   │                │
     │◄────────────────┤                │                │
     │                 │                │                │
     │ Fill job details│                │                │
     │ - Title         │                │                │
     │ - Description   │                │                │
     │ - Requirements  │                │                │
     │ - Salary range  │                │                │
     ├────────────────►│                │                │
     │                 │                │                │
     │ Click "Create"  │                │                │
     ├────────────────►│                │                │
     │                 │ POST /api/v1   │                │
     │                 │ /jobs          │                │
     │                 ├───────────────►│                │
     │                 │                │ Validate data  │
     │                 │                │ (Pydantic)     │
     │                 │                │                │
     │                 │                │ INSERT job     │
     │                 │                ├───────────────►│
     │                 │                │◄───────────────┤
     │                 │                │ Job created    │
     │                 │                │                │
     │                 │                │ Extract skills │
     │                 │                │ for embedding  │
     │                 │                │                │
     │                 │◄───────────────┤                │
     │                 │ 201 Created    │                │
     │◄────────────────┤                │                │
     │ Success message │                │                │
     │                 │                │                │
```

### Update Job Status

```
┌──────────┐      ┌─────────┐      ┌─────────┐      ┌─────────┐
│Recruiter │      │Frontend │      │ Backend │      │Database │
└────┬─────┘      └────┬────┘      └────┬────┘      └────┬────┘
     │                 │                │                │
     │ Select job &    │                │                │
     │ change status   │                │                │
     │ (draft→active)  │                │                │
     ├────────────────►│                │                │
     │                 │                │                │
     │                 │ POST /api/v1   │                │
     │                 │ /jobs/{id}     │                │
     │                 │ /activate      │                │
     │                 ├───────────────►│                │
     │                 │                │ UPDATE job     │
     │                 │                │ SET status=    │
     │                 │                │ 'active'       │
     │                 │                ├───────────────►│
     │                 │                │◄───────────────┤
     │                 │                │                │
     │                 │                │ Trigger events │
     │                 │                │ - Index for    │
     │                 │                │   search       │
     │                 │                │ - Notify team  │
     │                 │                │                │
     │                 │◄───────────────┤                │
     │                 │ Updated job    │                │
     │◄────────────────┤                │                │
     │                 │                │                │
```

## 3. Candidate Management Flow

### Add New Candidate

```
┌──────────┐      ┌─────────┐      ┌─────────┐      ┌─────────┐
│Recruiter │      │Frontend │      │ Backend │      │Database │
└────┬─────┘      └────┬────┘      └────┬────┘      └────┬────┘
     │                 │                │                │
     │ Click "Add      │                │                │
     │ Candidate"      │                │                │
     ├────────────────►│                │                │
     │                 │                │                │
     │ Fill candidate  │                │                │
     │ details         │                │                │
     │ - Name          │                │                │
     │ - Email         │                │                │
     │ - Experience    │                │                │
     │ - Skills        │                │                │
     ├────────────────►│                │                │
     │                 │                │                │
     │ Click "Create"  │                │                │
     ├────────────────►│                │                │
     │                 │ POST /api/v1   │                │
     │                 │ /candidates    │                │
     │                 ├───────────────►│                │
     │                 │                │ Validate email │
     │                 │                │ uniqueness     │
     │                 │                │                │
     │                 │                │ Check for      │
     │                 │                │ duplicates     │
     │                 │                ├───────────────►│
     │                 │                │◄───────────────┤
     │                 │                │                │
     │                 │                │ CREATE         │
     │                 │                │ candidate      │
     │                 │                ├───────────────►│
     │                 │                │◄───────────────┤
     │                 │                │                │
     │                 │◄───────────────┤                │
     │                 │ 201 Created    │                │
     │◄────────────────┤                │                │
     │                 │                │                │
```

## 4. Resume Upload & Processing Flow

```
┌──────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
│Recruiter │   │Frontend │   │ Backend │   │Database │   │Vector DB│
└────┬─────┘   └────┬────┘   └────┬────┘   └────┬────┘   └────┬────┘
     │              │             │             │             │
     │ Select resume│             │             │             │
     │ file (PDF)   │             │             │             │
     ├─────────────►│             │             │             │
     │              │             │             │             │
     │              │ POST /api/v1│             │             │
     │              │ /candidates │             │             │
     │              │ /{id}/resumes             │             │
     │              ├────────────►│             │             │
     │              │ (multipart  │             │             │
     │              │ form-data)  │             │             │
     │              │             │ Save file   │             │
     │              │             │ to storage  │             │
     │              │             │             │             │
     │              │             │ CREATE      │             │
     │              │             │ resume      │             │
     │              │             │ record      │             │
     │              │             ├────────────►│             │
     │              │             │◄────────────┤             │
     │              │             │             │             │
     │              │◄────────────┤             │             │
     │              │ 201 Created │             │             │
     │◄─────────────┤             │             │             │
     │              │             │             │             │
     │              │             │ [Background Task Starts]  │
     │              │             │             │             │
     │              │             │ Extract text│             │
     │              │             │ from PDF    │             │
     │              │             │             │             │
     │              │             │ UPDATE      │             │
     │              │             │ raw_text    │             │
     │              │             ├────────────►│             │
     │              │             │             │             │
     │              │             │ Chunk text  │             │
     │              │             │ (512 tokens)│             │
     │              │             │             │             │
     │              │             │ CREATE      │             │
     │              │             │ chunks      │             │
     │              │             ├────────────►│             │
     │              │             │             │             │
     │              │             │ Generate    │             │
     │              │             │ embeddings  │             │
     │              │             │ (LLM API)   │             │
     │              │             │             │             │
     │              │             │ Store       │             │
     │              │             │ vectors     │             │
     │              │             ├─────────────────────────►│
     │              │             │             │             │
     │              │             │ UPDATE      │             │
     │              │             │ is_embedded │             │
     │              │             ├────────────►│             │
     │              │             │             │             │
     │              │             │ [Task Complete]           │
     │              │             │             │             │
```

## 5. Candidate-Job Matching Flow (RAG)

```
┌──────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌──────┐
│Recruiter │   │Frontend │   │ Backend │   │Vector DB│   │ Database│   │ LLM  │
└────┬─────┘   └────┬────┘   └────┬────┘   └────┬────┘   └────┬────┘   └──┬───┘
     │              │             │             │             │            │
     │ View job &   │             │             │             │            │
     │ click "Find  │             │             │             │            │
     │ Matches"     │             │             │             │            │
     ├─────────────►│             │             │             │            │
     │              │ POST /api/v1│             │             │            │
     │              │ /jobs/{id}  │             │             │            │
     │              │ /match      │             │             │            │
     │              ├────────────►│             │             │            │
     │              │             │ Get job     │             │            │
     │              │             │ details     │             │            │
     │              │             ├─────────────────────────►│            │
     │              │             │◄─────────────────────────┤            │
     │              │             │             │             │            │
     │              │             │ Generate    │             │            │
     │              │             │ job query   │             │            │
     │              │             │ embedding   │             │            │
     │              │             ├─────────────────────────────────────►│
     │              │             │◄─────────────────────────────────────┤
     │              │             │             │             │            │
     │              │             │ Vector      │             │            │
     │              │             │ search      │             │            │
     │              │             ├────────────►│             │            │
     │              │             │◄────────────┤             │            │
     │              │             │ Top-K       │             │            │
     │              │             │ candidates  │             │            │
     │              │             │             │             │            │
     │              │             │ Apply       │             │            │
     │              │             │ filters     │             │            │
     │              │             │ (exp, loc)  │             │            │
     │              │             │             │             │            │
     │              │             │ Get full    │             │            │
     │              │             │ candidate   │             │            │
     │              │             │ details     │             │            │
     │              │             ├─────────────────────────►│            │
     │              │             │◄─────────────────────────┤            │
     │              │             │             │             │            │
     │              │             │ Generate    │             │            │
     │              │             │ match       │             │            │
     │              │             │ explanation │             │            │
     │              │             ├─────────────────────────────────────►│
     │              │             │ "Candidate X matches because..."    │
     │              │             │◄─────────────────────────────────────┤
     │              │             │             │             │            │
     │              │             │ CREATE      │             │            │
     │              │             │ job_        │             │            │
     │              │             │ recommendation            │            │
     │              │             ├─────────────────────────►│            │
     │              │             │             │             │            │
     │              │◄────────────┤             │             │            │
     │              │ Ranked list │             │             │            │
     │              │ with scores │             │             │            │
     │◄─────────────┤             │             │             │            │
     │ Display      │             │             │             │            │
     │ matches      │             │             │             │            │
     │              │             │             │             │            │
```

## 6. Application Submission Flow

```
┌──────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
│Candidate │   │Frontend │   │ Backend │   │Database │
│(External)│   │         │   │         │   │         │
└────┬─────┘   └────┬────┘   └────┬────┘   └────┬────┘
     │              │             │             │
     │ View job     │             │             │
     │ posting      │             │             │
     │ (public page)│             │             │
     ├─────────────►│             │             │
     │              │             │             │
     │ Click "Apply"│             │             │
     ├─────────────►│             │             │
     │              │             │             │
     │ Fill form    │             │             │
     │ - Resume     │             │             │
     │ - Cover      │             │             │
     │   letter     │             │             │
     ├─────────────►│             │             │
     │              │             │             │
     │ Submit       │             │             │
     ├─────────────►│             │             │
     │              │ POST /api/v1│             │
     │              │ /applications            │
     │              ├────────────►│             │
     │              │             │ Check       │
     │              │             │ candidate   │
     │              │             │ exists      │
     │              │             ├────────────►│
     │              │             │◄────────────┤
     │              │             │             │
     │              │             │ CREATE      │
     │              │             │ candidate   │
     │              │             │ if new      │
     │              │             ├────────────►│
     │              │             │             │
     │              │             │ Process     │
     │              │             │ resume      │
     │              │             │             │
     │              │             │ Calculate   │
     │              │             │ match score │
     │              │             │             │
     │              │             │ CREATE      │
     │              │             │ application │
     │              │             │ (status:    │
     │              │             │ submitted)  │
     │              │             ├────────────►│
     │              │             │             │
     │              │             │ Send email  │
     │              │             │ confirmation│
     │              │             │             │
     │              │◄────────────┤             │
     │              │ 201 Created │             │
     │◄─────────────┤             │             │
     │ Confirmation │             │             │
     │ message      │             │             │
     │              │             │             │
```

## 7. Application Review Flow

```
┌──────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
│Recruiter │   │Frontend │   │ Backend │   │Database │
└────┬─────┘   └────┬────┘   └────┬────┘   └────┬────┘
     │              │             │             │
     │ View         │             │             │
     │ applications │             │             │
     │ for job      │             │             │
     ├─────────────►│             │             │
     │              │ GET /api/v1 │             │
     │              │ /jobs/{id}  │             │
     │              │ /applications             │
     │              ├────────────►│             │
     │              │             │ Query with  │
     │              │             │ filters     │
     │              │             ├────────────►│
     │              │             │◄────────────┤
     │              │◄────────────┤             │
     │              │ Application │             │
     │              │ list with   │             │
     │              │ scores      │             │
     │◄─────────────┤             │             │
     │              │             │             │
     │ Select       │             │             │
     │ candidate    │             │             │
     ├─────────────►│             │             │
     │              │             │             │
     │ View full    │             │             │
     │ profile &    │             │             │
     │ resume       │             │             │
     ├─────────────►│             │             │
     │              │ GET /api/v1 │             │
     │              │ /applications             │
     │              │ /{id}       │             │
     │              ├────────────►│             │
     │              │             │ Get full    │
     │              │             │ details     │
     │              │             ├────────────►│
     │              │             │◄────────────┤
     │              │◄────────────┤             │
     │◄─────────────┤             │             │
     │              │             │             │
     │ Update status│             │             │
     │ to           │             │             │
     │ "shortlisted"│             │             │
     ├─────────────►│             │             │
     │              │ PATCH       │             │
     │              │ /api/v1     │             │
     │              │ /applications             │
     │              │ /{id}       │             │
     │              ├────────────►│             │
     │              │             │ UPDATE      │
     │              │             │ status      │
     │              │             ├────────────►│
     │              │             │             │
     │              │             │ CREATE      │
     │              │             │ status      │
     │              │             │ history     │
     │              │             ├────────────►│
     │              │             │             │
     │              │             │ Send email  │
     │              │             │ to candidate│
     │              │             │             │
     │              │◄────────────┤             │
     │◄─────────────┤             │             │
     │              │             │             │
```

## 8. Interview Scheduling Flow

```
┌──────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
│Recruiter │   │Frontend │   │ Backend │   │Database │
└────┬─────┘   └────┬────┘   └────┬────┘   └────┬────┘
     │              │             │             │
     │ Select       │             │             │
     │ shortlisted  │             │             │
     │ candidate    │             │             │
     ├─────────────►│             │             │
     │              │             │             │
     │ Click        │             │             │
     │ "Schedule    │             │             │
     │ Interview"   │             │             │
     ├─────────────►│             │             │
     │              │             │             │
     │ Fill details │             │             │
     │ - Date/Time  │             │             │
     │ - Type       │             │             │
     │ - Interviewer│             │             │
     │ - Link/Loc   │             │             │
     ├─────────────►│             │             │
     │              │ POST /api/v1│             │
     │              │ /interviews │             │
     │              ├────────────►│             │
     │              │             │ CREATE      │
     │              │             │ interview   │
     │              │             ├────────────►│
     │              │             │             │
     │              │             │ UPDATE      │
     │              │             │ application │
     │              │             │ status      │
     │              │             ├────────────►│
     │              │             │             │
     │              │             │ Send emails │
     │              │             │ - Candidate │
     │              │             │ - Interviewer│
     │              │             │             │
     │              │             │ Create      │
     │              │             │ calendar    │
     │              │             │ invites     │
     │              │             │             │
     │              │◄────────────┤             │
     │◄─────────────┤             │             │
     │ Confirmation │             │             │
     │              │             │             │
```

## 9. Complete Hiring Workflow

```
Application Status Flow:

┌─────────────┐
│  submitted  │ (Initial state when candidate applies)
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ under_review│ (Recruiter reviewing application)
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ shortlisted │ (Candidate passes initial screening)
└──────┬──────┘
       │
       ├──────────────────────────┐
       ↓                          ↓
┌─────────────┐          ┌──────────────┐
│ interview_  │          │  rejected    │ (Not suitable)
│ scheduled   │          └──────────────┘
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ interview_  │ (Interview completed)
│ completed   │
└──────┬──────┘
       │
       ├──────────────────────────┐
       ↓                          ↓
┌─────────────┐          ┌──────────────┐
│offer_       │          │  rejected    │
│extended     │          └──────────────┘
└──────┬──────┘
       │
       ├──────────────────────────┐
       ↓                          ↓
┌─────────────┐          ┌──────────────┐
│offer_       │          │offer_        │
│accepted     │          │rejected      │
└──────┬──────┘          └──────────────┘
       │
       ↓
┌─────────────┐
│   hired     │ (Final state - candidate hired)
└─────────────┘
```

## 10. Data Synchronization Flow

```
┌──────────────────────────────────────────────────────────┐
│            Data Flow Between Components                   │
│                                                            │
│  Frontend ──► Backend ──► PostgreSQL                      │
│                    │                                       │
│                    ├──► Vector DB (Resume embeddings)     │
│                    │                                       │
│                    ├──► LLM API (Match generation)        │
│                    │                                       │
│                    └──► File Storage (Resume files)       │
│                                                            │
│  Real-time updates:                                       │
│  - WebSocket for live notifications (future)              │
│  - Polling for status updates (current)                   │
│  - Server-sent events for async tasks (future)           │
└──────────────────────────────────────────────────────────┘
```

---

**Note**: These flows represent the current implementation. Some features like email notifications and calendar integration are planned for future releases.

**Last Updated**: 2025-10-02
