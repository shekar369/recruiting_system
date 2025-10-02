"""
Admin endpoints for batch operations and system management
"""
import logging
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from celery.result import AsyncResult
from pydantic import BaseModel

from app.database import get_db
from app.workers.embedding_tasks import batch_embed_candidates, reindex_all

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


class BatchEmbedRequest(BaseModel):
    """Request model for batch embedding"""
    candidate_ids: Optional[List[UUID]] = None
    batch_size: int = 100


@router.post("/batch-embed")
async def start_batch_embedding(
    request: BatchEmbedRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Start batch embedding for multiple candidates

    Args:
        request: Batch embed request with optional candidate IDs
        db: Database session

    Returns:
        Task information
    """
    try:
        # Convert UUIDs to strings for Celery
        candidate_ids = [str(cid) for cid in request.candidate_ids] if request.candidate_ids else None

        # Trigger batch embedding task
        task = batch_embed_candidates.delay(
            candidate_ids=candidate_ids,
            batch_size=request.batch_size
        )

        return {
            "task_id": task.id,
            "status": "started",
            "message": f"Batch embedding started for {len(request.candidate_ids) if request.candidate_ids else 'all'} candidates",
            "batch_size": request.batch_size
        }

    except Exception as e:
        logger.error(f"Error starting batch embedding: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting batch embedding: {str(e)}"
        )


@router.get("/batch-status/{task_id}")
async def get_batch_status(task_id: str):
    """
    Get the status of a batch processing task

    Args:
        task_id: Celery task ID

    Returns:
        Task status and progress
    """
    try:
        task_result = AsyncResult(task_id)

        response = {
            "task_id": task_id,
            "status": task_result.state,
        }

        if task_result.state == 'PENDING':
            response["message"] = "Task is pending"
            response["current"] = 0
            response["total"] = 0
        elif task_result.state == 'PROGRESS':
            response["message"] = "Task is in progress"
            info = task_result.info or {}
            response["current"] = info.get('current', 0)
            response["total"] = info.get('total', 0)
            response["successful"] = info.get('successful', 0)
            response["failed"] = info.get('failed', 0)
            response["status_message"] = info.get('status', '')
        elif task_result.state == 'SUCCESS':
            response["message"] = "Task completed successfully"
            result = task_result.result or {}
            response["total_candidates"] = result.get('total_candidates', 0)
            response["successful"] = result.get('successful', 0)
            response["failed"] = result.get('failed', 0)
            response["failed_candidates"] = result.get('failed_candidates', [])
        elif task_result.state == 'FAILURE':
            response["message"] = "Task failed"
            response["error"] = str(task_result.info)

        return response

    except Exception as e:
        logger.error(f"Error getting batch status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting batch status: {str(e)}"
        )


@router.post("/batch-cancel/{task_id}")
async def cancel_batch_task(task_id: str):
    """
    Cancel a batch processing task

    Args:
        task_id: Celery task ID

    Returns:
        Cancellation status
    """
    try:
        task_result = AsyncResult(task_id)

        if task_result.state in ['SUCCESS', 'FAILURE']:
            return {
                "task_id": task_id,
                "status": "already_completed",
                "message": f"Task already completed with status: {task_result.state}"
            }

        task_result.revoke(terminate=True)

        return {
            "task_id": task_id,
            "status": "cancelled",
            "message": "Task cancellation requested"
        }

    except Exception as e:
        logger.error(f"Error cancelling task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cancelling task: {str(e)}"
        )


@router.post("/reindex-all")
async def reindex_all_candidates():
    """
    Reindex all candidates - rebuilds the entire FAISS index

    Warning: This will clear the existing index and reprocess all candidates

    Returns:
        Task information
    """
    try:
        task = reindex_all.delay()

        return {
            "task_id": task.id,
            "status": "started",
            "message": "Full reindexing started. This will take a while.",
            "warning": "Existing FAISS index has been cleared"
        }

    except Exception as e:
        logger.error(f"Error starting reindex: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting reindex: {str(e)}"
        )


@router.get("/vector-stats")
async def get_vector_stats():
    """
    Get statistics about the vector index

    Returns:
        Vector index statistics
    """
    try:
        from app.services.vector_service import get_vector_service

        vector_service = get_vector_service()
        stats = vector_service.get_index_stats()

        return {
            **stats,
            "message": "Vector index statistics"
        }

    except Exception as e:
        logger.error(f"Error getting vector stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting vector stats: {str(e)}"
        )


@router.get("/embedding-model-info")
async def get_embedding_model_info():
    """
    Get information about the embedding model

    Returns:
        Embedding model information
    """
    try:
        from app.services.embedding_service import get_embedding_service

        embedding_service = get_embedding_service()
        info = embedding_service.get_model_info()

        return {
            **info,
            "message": "Embedding model information"
        }

    except Exception as e:
        logger.error(f"Error getting embedding model info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting embedding model info: {str(e)}"
        )
