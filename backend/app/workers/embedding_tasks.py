"""
Celery tasks for batch embedding processing
"""
import logging
from typing import List
from uuid import UUID
import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.celery_app import celery_app
from app.config import settings
from app.models.candidate import Candidate, CandidateResume
from app.workers.resume_tasks import process_resume

logger = logging.getLogger(__name__)


# Create async engine for Celery tasks
engine = create_async_engine(settings.ASYNC_DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


@celery_app.task(bind=True, name='app.workers.embedding_tasks.batch_embed_candidates')
def batch_embed_candidates(self, candidate_ids: List[str] = None, batch_size: int = 100):
    """
    Batch process embeddings for multiple candidates

    Args:
        candidate_ids: Optional list of specific candidate IDs to process
        batch_size: Number of candidates to process in each batch
    """
    try:
        # Update task state
        self.update_state(state='PROGRESS', meta={
            'status': 'Starting batch embedding',
            'current': 0,
            'total': 0
        })

        # Run async processing
        result = asyncio.run(_batch_embed_async(
            candidate_ids=[UUID(cid) for cid in candidate_ids] if candidate_ids else None,
            batch_size=batch_size,
            task=self
        ))

        return result

    except Exception as e:
        logger.error(f"Error in batch embedding: {e}")
        raise


async def _batch_embed_async(
    candidate_ids: List[UUID] = None,
    batch_size: int = 100,
    task=None
) -> dict:
    """Async implementation of batch embedding"""
    async with AsyncSessionLocal() as db:
        try:
            # Get candidates to process
            if candidate_ids:
                stmt = select(Candidate).where(Candidate.id.in_(candidate_ids))
            else:
                # Get all active candidates
                stmt = select(Candidate).where(Candidate.status == 'active')

            result = await db.execute(stmt)
            candidates = result.scalars().all()

            total_candidates = len(candidates)
            logger.info(f"Starting batch embedding for {total_candidates} candidates")

            if task:
                task.update_state(state='PROGRESS', meta={
                    'status': 'Processing candidates',
                    'current': 0,
                    'total': total_candidates,
                    'successful': 0,
                    'failed': 0
                })

            successful = 0
            failed = 0
            failed_candidates = []

            # Process in batches
            for i in range(0, total_candidates, batch_size):
                batch = candidates[i:i + batch_size]

                for candidate in batch:
                    try:
                        # Get the candidate's latest resume
                        stmt = select(CandidateResume).where(
                            CandidateResume.candidate_id == candidate.id
                        ).order_by(CandidateResume.created_at.desc()).limit(1)

                        result = await db.execute(stmt)
                        resume = result.scalar_one_or_none()

                        if not resume or not resume.file_path:
                            logger.warning(f"No resume found for candidate {candidate.id}")
                            continue

                        # Trigger resume processing task
                        process_resume.delay(
                            resume_id=str(resume.id),
                            file_path=resume.file_path
                        )

                        successful += 1

                    except Exception as e:
                        logger.error(f"Error processing candidate {candidate.id}: {e}")
                        failed += 1
                        failed_candidates.append({
                            'candidate_id': str(candidate.id),
                            'error': str(e)
                        })

                    # Update progress
                    if task:
                        current = i + (candidates.index(candidate) - i) + 1
                        task.update_state(state='PROGRESS', meta={
                            'status': f'Processing candidate {current}/{total_candidates}',
                            'current': current,
                            'total': total_candidates,
                            'successful': successful,
                            'failed': failed
                        })

            logger.info(f"Batch embedding completed: {successful} successful, {failed} failed")

            return {
                'status': 'completed',
                'total_candidates': total_candidates,
                'successful': successful,
                'failed': failed,
                'failed_candidates': failed_candidates
            }

        except Exception as e:
            logger.error(f"Error in batch embedding async: {e}")
            raise


@celery_app.task(bind=True, name='app.workers.embedding_tasks.reindex_all')
def reindex_all(self):
    """
    Reindex all candidates - useful after system maintenance

    This will:
    1. Clear the existing FAISS index
    2. Re-embed all candidates
    3. Rebuild the vector index
    """
    try:
        from app.services.vector_service import get_vector_service
        import shutil
        from pathlib import Path

        # Clear existing index
        self.update_state(state='PROGRESS', meta={'status': 'Clearing existing index'})

        vector_service = get_vector_service()
        index_path = Path(vector_service.index_path)

        if index_path.exists():
            index_path.unlink()
            logger.info("Deleted existing FAISS index")

        metadata_path = index_path.parent / "faiss_metadata.json"
        if metadata_path.exists():
            metadata_path.unlink()
            logger.info("Deleted existing metadata")

        # Reinitialize vector service
        from app.services import vector_service as vs_module
        vs_module._vector_service_instance = None
        vector_service = get_vector_service()

        # Trigger batch embedding for all candidates
        self.update_state(state='PROGRESS', meta={'status': 'Starting reindexing'})

        result = batch_embed_candidates.delay(candidate_ids=None, batch_size=50)

        return {
            'status': 'reindexing',
            'batch_task_id': result.id,
            'message': 'Reindexing started. Use batch_task_id to check progress.'
        }

    except Exception as e:
        logger.error(f"Error in reindex_all: {e}")
        raise
