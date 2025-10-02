"""
Resume processing endpoints
"""
import logging
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from celery.result import AsyncResult

from app.database import get_db
from app.models.candidate import Candidate, CandidateResume
from app.workers.resume_tasks import process_resume

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.post("/{candidate_id}/upload", status_code=status.HTTP_201_CREATED)
async def upload_resume(
    candidate_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload a resume file for a candidate

    Args:
        candidate_id: Candidate UUID
        file: Resume file (PDF or DOCX)
        db: Database session

    Returns:
        Resume record with task_id for processing status
    """
    try:
        # Verify candidate exists
        stmt = select(Candidate).where(Candidate.id == candidate_id)
        result = await db.execute(stmt)
        candidate = result.scalar_one_or_none()

        if not candidate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Candidate {candidate_id} not found"
            )

        # Validate file type
        allowed_types = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {file.content_type}. Only PDF and DOCX are supported."
            )

        # Save file to uploads directory
        import os
        from pathlib import Path

        upload_dir = Path("uploads/resumes")
        upload_dir.mkdir(parents=True, exist_ok=True)

        file_extension = Path(file.filename).suffix
        file_path = upload_dir / f"{candidate_id}{file_extension}"

        # Write file
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        # Create resume record
        resume = CandidateResume(
            candidate_id=candidate_id,
            file_name=file.filename,
            file_path=str(file_path),
            file_size=len(contents),
            mime_type=file.content_type
        )
        db.add(resume)
        await db.flush()

        # Trigger async processing
        task = process_resume.delay(
            resume_id=str(resume.id),
            file_path=str(file_path)
        )

        await db.commit()

        return {
            "id": resume.id,
            "candidate_id": resume.candidate_id,
            "file_name": resume.file_name,
            "file_size": resume.file_size,
            "task_id": task.id,
            "status": "processing",
            "message": "Resume uploaded successfully. Processing in background."
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error uploading resume: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading resume: {str(e)}"
        )


@router.get("/{resume_id}/status")
async def get_processing_status(
    resume_id: UUID,
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get the processing status of a resume

    Args:
        resume_id: Resume UUID
        task_id: Celery task ID
        db: Database session

    Returns:
        Processing status and results
    """
    try:
        # Get resume record
        stmt = select(CandidateResume).where(CandidateResume.id == resume_id)
        result = await db.execute(stmt)
        resume = result.scalar_one_or_none()

        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resume {resume_id} not found"
            )

        # Get task status
        task_result = AsyncResult(task_id)

        response = {
            "resume_id": resume_id,
            "task_id": task_id,
            "status": task_result.state,
            "file_name": resume.file_name,
        }

        if task_result.state == 'PENDING':
            response["message"] = "Task is pending"
        elif task_result.state == 'PROGRESS':
            response["message"] = "Task is in progress"
            response["meta"] = task_result.info
        elif task_result.state == 'SUCCESS':
            response["message"] = "Processing completed successfully"
            response["result"] = task_result.result
        elif task_result.state == 'FAILURE':
            response["message"] = "Processing failed"
            response["error"] = str(task_result.info)

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting processing status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting processing status: {str(e)}"
        )


@router.post("/{resume_id}/reprocess")
async def reprocess_resume(
    resume_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Reprocess an existing resume

    Args:
        resume_id: Resume UUID
        db: Database session

    Returns:
        New task information
    """
    try:
        # Get resume record
        stmt = select(CandidateResume).where(CandidateResume.id == resume_id)
        result = await db.execute(stmt)
        resume = result.scalar_one_or_none()

        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resume {resume_id} not found"
            )

        if not resume.file_path:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resume file path not found"
            )

        # Trigger async processing
        task = process_resume.delay(
            resume_id=str(resume.id),
            file_path=resume.file_path
        )

        return {
            "resume_id": resume_id,
            "task_id": task.id,
            "status": "processing",
            "message": "Resume reprocessing started"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reprocessing resume: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reprocessing resume: {str(e)}"
        )


@router.get("/{resume_id}/chunks")
async def get_resume_chunks(
    resume_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all chunks for a resume

    Args:
        resume_id: Resume UUID
        db: Database session

    Returns:
        List of chunks
    """
    try:
        from app.models.vector import ResumeChunk

        stmt = select(ResumeChunk).where(
            ResumeChunk.resume_id == resume_id
        ).order_by(ResumeChunk.chunk_order)

        result = await db.execute(stmt)
        chunks = result.scalars().all()

        return {
            "resume_id": resume_id,
            "total_chunks": len(chunks),
            "chunks": [
                {
                    "id": chunk.id,
                    "chunk_text": chunk.chunk_text[:200] + "..." if len(chunk.chunk_text) > 200 else chunk.chunk_text,
                    "chunk_type": chunk.chunk_type,
                    "chunk_order": chunk.chunk_order,
                    "metadata": chunk.metadata,
                    "created_at": chunk.created_at
                }
                for chunk in chunks
            ]
        }

    except Exception as e:
        logger.error(f"Error getting resume chunks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting resume chunks: {str(e)}"
        )
