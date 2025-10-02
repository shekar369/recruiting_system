from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.candidate import Candidate
from app.schemas.candidate import (
    CandidateCreate,
    CandidateUpdate,
    CandidateResponse,
    CandidateListResponse
)

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.post("/", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
async def create_candidate(
    candidate: CandidateCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new candidate.

    - **first_name**: Candidate's first name (required)
    - **last_name**: Candidate's last name (required)
    - **email**: Unique email address (required)
    - **phone**: Contact phone number
    - **location**: Location/city
    - Other professional and personal details
    """
    # Check if email already exists
    stmt = select(Candidate).where(Candidate.email == candidate.email)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Candidate with email {candidate.email} already exists"
        )

    # Create new candidate
    db_candidate = Candidate(**candidate.model_dump())
    db.add(db_candidate)
    await db.commit()
    await db.refresh(db_candidate)

    return db_candidate


@router.get("/", response_model=CandidateListResponse)
async def list_candidates(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    status: str = Query(None, description="Filter by status"),
    location: str = Query(None, description="Filter by location"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a paginated list of candidates.

    - **page**: Page number (default: 1)
    - **size**: Items per page (default: 10, max: 100)
    - **status**: Filter by candidate status
    - **location**: Filter by location
    """
    # Build query
    stmt = select(Candidate)

    # Apply filters
    if status:
        stmt = stmt.where(Candidate.status == status)
    if location:
        stmt = stmt.where(Candidate.location.ilike(f"%{location}%"))

    # Get total count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar()

    # Apply pagination
    offset = (page - 1) * size
    stmt = stmt.offset(offset).limit(size).order_by(Candidate.created_at.desc())

    # Execute query
    result = await db.execute(stmt)
    candidates = result.scalars().all()

    return CandidateListResponse(
        total=total,
        page=page,
        size=size,
        candidates=candidates
    )


@router.get("/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(
    candidate_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific candidate by ID.

    - **candidate_id**: UUID of the candidate
    """
    stmt = select(Candidate).where(Candidate.id == candidate_id)
    result = await db.execute(stmt)
    candidate = result.scalar_one_or_none()

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with id {candidate_id} not found"
        )

    return candidate


@router.put("/{candidate_id}", response_model=CandidateResponse)
async def update_candidate(
    candidate_id: UUID,
    candidate_update: CandidateUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a candidate's information.

    - **candidate_id**: UUID of the candidate
    - Provide only the fields you want to update
    """
    # Get existing candidate
    stmt = select(Candidate).where(Candidate.id == candidate_id)
    result = await db.execute(stmt)
    db_candidate = result.scalar_one_or_none()

    if not db_candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with id {candidate_id} not found"
        )

    # Check email uniqueness if updating email
    if candidate_update.email and candidate_update.email != db_candidate.email:
        email_stmt = select(Candidate).where(Candidate.email == candidate_update.email)
        email_result = await db.execute(email_stmt)
        existing = email_result.scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email {candidate_update.email} is already in use"
            )

    # Update fields
    update_data = candidate_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_candidate, field, value)

    await db.commit()
    await db.refresh(db_candidate)

    return db_candidate


@router.patch("/{candidate_id}", response_model=CandidateResponse)
async def partial_update_candidate(
    candidate_id: UUID,
    candidate_update: CandidateUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Partially update a candidate (alias for PUT, supports partial updates).

    - **candidate_id**: UUID of the candidate
    - Provide only the fields you want to update
    """
    return await update_candidate(candidate_id, candidate_update, db)


@router.delete("/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_candidate(
    candidate_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a candidate.

    - **candidate_id**: UUID of the candidate
    - This will cascade delete all related data (resumes, skills, etc.)
    """
    stmt = select(Candidate).where(Candidate.id == candidate_id)
    result = await db.execute(stmt)
    db_candidate = result.scalar_one_or_none()

    if not db_candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with id {candidate_id} not found"
        )

    await db.delete(db_candidate)
    await db.commit()

    return None


@router.get("/email/{email}", response_model=CandidateResponse)
async def get_candidate_by_email(
    email: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a candidate by email address.

    - **email**: Email address of the candidate
    """
    stmt = select(Candidate).where(Candidate.email == email)
    result = await db.execute(stmt)
    candidate = result.scalar_one_or_none()

    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate with email {email} not found"
        )

    return candidate
