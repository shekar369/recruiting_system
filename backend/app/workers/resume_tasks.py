"""
Celery tasks for resume processing
"""
import logging
from typing import Dict, Any
from uuid import UUID
import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.celery_app import celery_app
from app.config import settings
from app.services.document_processor import document_processor
from app.services.chunking_service import chunking_service
from app.services.embedding_service import get_embedding_service
from app.services.vector_service import get_vector_service
from app.models.candidate import CandidateResume, Candidate
from app.models.vector import ResumeChunk, ChunkEmbedding

logger = logging.getLogger(__name__)


# Create async engine for Celery tasks
engine = create_async_engine(settings.ASYNC_DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


@celery_app.task(bind=True, name='app.workers.resume_tasks.process_resume')
def process_resume(self, resume_id: str, file_path: str):
    """
    Process a resume: extract text, parse, chunk, embed, and index

    Args:
        resume_id: Resume UUID as string
        file_path: Path to the resume file
    """
    try:
        # Update task state
        self.update_state(state='PROGRESS', meta={'status': 'Starting resume processing'})

        # Run async processing
        result = asyncio.run(_process_resume_async(
            resume_id=UUID(resume_id),
            file_path=file_path,
            task=self
        ))

        return result

    except Exception as e:
        logger.error(f"Error processing resume {resume_id}: {e}")
        raise


async def _process_resume_async(resume_id: UUID, file_path: str, task) -> Dict[str, Any]:
    """Async implementation of resume processing"""
    async with AsyncSessionLocal() as db:
        try:
            # Step 1: Extract and parse resume text
            task.update_state(state='PROGRESS', meta={'status': 'Extracting text from resume'})
            parsed_data = await document_processor.parse_resume(file_path)

            # Step 2: Update resume record with parsed data
            task.update_state(state='PROGRESS', meta={'status': 'Saving parsed data'})
            stmt = select(CandidateResume).where(CandidateResume.id == resume_id)
            result = await db.execute(stmt)
            resume = result.scalar_one_or_none()

            if not resume:
                raise ValueError(f"Resume {resume_id} not found")

            # Update parsed_data field
            resume.parsed_data = {
                'email': parsed_data.get('email'),
                'phone': parsed_data.get('phone'),
                'linkedin_url': parsed_data.get('linkedin_url'),
                'github_url': parsed_data.get('github_url'),
                'skills': parsed_data.get('skills', []),
                'full_text_length': len(parsed_data.get('full_text', '')),
                'has_experience': parsed_data.get('experience_section') is not None,
                'has_education': parsed_data.get('education_section') is not None,
            }
            await db.commit()

            # Step 3: Semantic chunking
            task.update_state(state='PROGRESS', meta={'status': 'Chunking resume text'})
            chunks = chunking_service.semantic_chunk_resume(parsed_data, preserve_sections=True)

            if not chunks:
                logger.warning(f"No chunks generated for resume {resume_id}")
                return {'status': 'completed', 'chunks_created': 0}

            # Step 4: Save chunks to database
            task.update_state(state='PROGRESS', meta={'status': f'Saving {len(chunks)} chunks'})
            chunk_records = []
            for chunk_data in chunks:
                chunk = ResumeChunk(
                    resume_id=resume_id,
                    candidate_id=resume.candidate_id,
                    chunk_text=chunk_data['chunk_text'],
                    chunk_type=chunk_data['chunk_type'],
                    chunk_order=chunk_data['chunk_order'],
                    metadata=chunk_data.get('metadata', {})
                )
                db.add(chunk)
                chunk_records.append(chunk)

            await db.flush()  # Flush to get chunk IDs

            # Step 5: Generate embeddings
            task.update_state(state='PROGRESS', meta={'status': 'Generating embeddings'})
            embedding_service = get_embedding_service()

            chunk_texts = [chunk.chunk_text for chunk in chunk_records]
            embeddings = embedding_service.embed_batch(chunk_texts, batch_size=32, show_progress=False)

            # Step 6: Save embeddings to database
            task.update_state(state='PROGRESS', meta={'status': 'Saving embeddings'})
            for chunk, embedding in zip(chunk_records, embeddings):
                chunk_embedding = ChunkEmbedding(
                    chunk_id=chunk.id,
                    embedding_vector=embedding.tolist(),  # Store as JSON array
                    embedding_model='all-MiniLM-L6-v2',
                    embedding_dimension=len(embedding)
                )
                db.add(chunk_embedding)

            await db.commit()

            # Step 7: Add to FAISS index
            task.update_state(state='PROGRESS', meta={'status': 'Adding to vector index'})
            vector_service = get_vector_service(dimension=384)

            metadata_list = [
                {
                    'chunk_id': str(chunk.id),
                    'candidate_id': str(chunk.candidate_id),
                    'resume_id': str(chunk.resume_id),
                    'chunk_type': chunk.chunk_type,
                    'chunk_order': chunk.chunk_order
                }
                for chunk in chunk_records
            ]

            vector_service.add_vectors(embeddings, metadata_list)
            vector_service.save_index()

            logger.info(f"Successfully processed resume {resume_id}: {len(chunks)} chunks created")

            return {
                'status': 'completed',
                'resume_id': str(resume_id),
                'chunks_created': len(chunks),
                'skills_found': len(parsed_data.get('skills', [])),
                'has_experience': parsed_data.get('experience_section') is not None,
                'has_education': parsed_data.get('education_section') is not None,
            }

        except Exception as e:
            await db.rollback()
            logger.error(f"Error in async resume processing: {e}")
            raise
