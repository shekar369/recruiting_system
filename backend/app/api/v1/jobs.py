from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.job import Job
from app.schemas.job import (
    JobCreate,
    JobUpdate,
    JobResponse,
    JobListResponse
)

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    job: JobCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new job posting.

    - **title**: Job title (required)
    - **description**: Job description (required)
    - **department**: Department name
    - **location**: Job location
    - **employment_type**: full-time, part-time, contract, internship
    - **work_mode**: remote, hybrid, onsite
    - Other job details
    """
    db_job = Job(**job.model_dump())
    db.add(db_job)
    await db.commit()
    await db.refresh(db_job)

    return db_job


@router.get("/", response_model=JobListResponse)
async def list_jobs(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    status: str = Query(None, description="Filter by status (draft, active, closed, on_hold)"),
    department: str = Query(None, description="Filter by department"),
    location: str = Query(None, description="Filter by location"),
    employment_type: str = Query(None, description="Filter by employment type"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a paginated list of jobs.

    - **page**: Page number (default: 1)
    - **size**: Items per page (default: 10, max: 100)
    - **status**: Filter by job status
    - **department**: Filter by department
    - **location**: Filter by location
    - **employment_type**: Filter by employment type
    """
    # Build query
    stmt = select(Job)

    # Apply filters
    if status:
        stmt = stmt.where(Job.status == status)
    if department:
        stmt = stmt.where(Job.department.ilike(f"%{department}%"))
    if location:
        stmt = stmt.where(Job.location.ilike(f"%{location}%"))
    if employment_type:
        stmt = stmt.where(Job.employment_type == employment_type)

    # Get total count
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar()

    # Apply pagination
    offset = (page - 1) * size
    stmt = stmt.offset(offset).limit(size).order_by(Job.created_at.desc())

    # Execute query
    result = await db.execute(stmt)
    jobs = result.scalars().all()

    return JobListResponse(
        total=total,
        page=page,
        size=size,
        jobs=jobs
    )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific job by ID.

    - **job_id**: UUID of the job
    """
    stmt = select(Job).where(Job.id == job_id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {job_id} not found"
        )

    return job


@router.put("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: UUID,
    job_update: JobUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a job posting.

    - **job_id**: UUID of the job
    - Provide only the fields you want to update
    """
    # Get existing job
    stmt = select(Job).where(Job.id == job_id)
    result = await db.execute(stmt)
    db_job = result.scalar_one_or_none()

    if not db_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {job_id} not found"
        )

    # Update fields
    update_data = job_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_job, field, value)

    await db.commit()
    await db.refresh(db_job)

    return db_job


@router.patch("/{job_id}", response_model=JobResponse)
async def partial_update_job(
    job_id: UUID,
    job_update: JobUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Partially update a job (alias for PUT, supports partial updates).

    - **job_id**: UUID of the job
    - Provide only the fields you want to update
    """
    return await update_job(job_id, job_update, db)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a job posting.

    - **job_id**: UUID of the job
    - This will cascade delete all related applications and recommendations
    """
    stmt = select(Job).where(Job.id == job_id)
    result = await db.execute(stmt)
    db_job = result.scalar_one_or_none()

    if not db_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {job_id} not found"
        )

    await db.delete(db_job)
    await db.commit()

    return None


@router.post("/{job_id}/activate", response_model=JobResponse)
async def activate_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Activate a job posting (change status to 'active').

    - **job_id**: UUID of the job
    """
    stmt = select(Job).where(Job.id == job_id)
    result = await db.execute(stmt)
    db_job = result.scalar_one_or_none()

    if not db_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {job_id} not found"
        )

    db_job.status = "active"
    from datetime import datetime
    db_job.posted_at = datetime.now()

    await db.commit()
    await db.refresh(db_job)

    return db_job


@router.post("/{job_id}/close", response_model=JobResponse)
async def close_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Close a job posting (change status to 'closed').

    - **job_id**: UUID of the job
    """
    stmt = select(Job).where(Job.id == job_id)
    result = await db.execute(stmt)
    db_job = result.scalar_one_or_none()

    if not db_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id {job_id} not found"
        )

    db_job.status = "closed"
    from datetime import datetime
    db_job.closed_at = datetime.now()

    await db.commit()
    await db.refresh(db_job)

    return db_job
