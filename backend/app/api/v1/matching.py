"""
Job-Candidate Matching endpoints
"""
import logging
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.job import Job, JobRecommendation
from app.models.candidate import Candidate
from app.services.matching_service import matching_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["matching"])


@router.post("/jobs/{job_id}/match")
async def match_candidates_to_job(
    job_id: UUID,
    top_k: int = 20,
    save_recommendations: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """
    Find and rank candidate matches for a job

    Args:
        job_id: Job ID to match candidates for
        top_k: Number of top matches to return
        save_recommendations: Whether to save recommendations to database
        db: Database session

    Returns:
        List of candidate matches with detailed scores
    """
    try:
        # Verify job exists
        stmt = select(Job).where(Job.id == job_id)
        result = await db.execute(stmt)
        job = result.scalar_one_or_none()

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found"
            )

        # Perform matching
        matches = await matching_service.match_candidates_to_job(
            db=db,
            job_id=job_id,
            top_k=top_k
        )

        # Save recommendations if requested
        if save_recommendations and matches:
            await matching_service.save_recommendations(
                db=db,
                job_id=job_id,
                matches=matches
            )

        return {
            'job_id': str(job_id),
            'job_title': job.title,
            'total_matches': len(matches),
            'matches': [match.to_dict() for match in matches],
            'recommendations_saved': save_recommendations
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error matching candidates to job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error matching candidates: {str(e)}"
        )


@router.get("/jobs/{job_id}/recommendations")
async def get_job_recommendations(
    job_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get saved recommendations for a job

    Args:
        job_id: Job ID
        db: Database session

    Returns:
        List of saved recommendations with candidate details
    """
    try:
        # Get recommendations
        stmt = select(JobRecommendation).where(
            JobRecommendation.job_id == job_id
        ).order_by(JobRecommendation.rank)

        result = await db.execute(stmt)
        recommendations = result.scalars().all()

        if not recommendations:
            return {
                'job_id': str(job_id),
                'total_recommendations': 0,
                'recommendations': [],
                'message': 'No recommendations found. Run matching first.'
            }

        # Get candidate details
        candidate_ids = [rec.candidate_id for rec in recommendations]
        stmt = select(Candidate).where(Candidate.id.in_(candidate_ids))
        result = await db.execute(stmt)
        candidates = {c.id: c for c in result.scalars().all()}

        # Build response
        recommendations_list = []
        for rec in recommendations:
            candidate = candidates.get(rec.candidate_id)
            if candidate:
                rec_dict = {
                    'rank': rec.rank,
                    'match_score': float(rec.match_score),
                    'candidate': {
                        'id': str(candidate.id),
                        'first_name': candidate.first_name,
                        'last_name': candidate.last_name,
                        'email': candidate.email,
                        'phone': candidate.phone,
                        'location': candidate.location,
                        'current_job_title': candidate.current_job_title,
                        'current_company': candidate.current_company,
                        'years_of_experience': candidate.years_of_experience,
                    },
                    'match_details': rec.match_details,
                    'created_at': rec.created_at.isoformat() if rec.created_at else None
                }
                recommendations_list.append(rec_dict)

        return {
            'job_id': str(job_id),
            'total_recommendations': len(recommendations_list),
            'recommendations': recommendations_list
        }

    except Exception as e:
        logger.error(f"Error getting job recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting recommendations: {str(e)}"
        )


@router.get("/candidates/{candidate_id}/recommendations")
async def get_candidate_recommendations(
    candidate_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get job recommendations for a candidate

    Args:
        candidate_id: Candidate ID
        db: Database session

    Returns:
        List of jobs that matched this candidate
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

        # Get recommendations
        stmt = select(JobRecommendation).where(
            JobRecommendation.candidate_id == candidate_id
        ).order_by(JobRecommendation.match_score.desc())

        result = await db.execute(stmt)
        recommendations = result.scalars().all()

        if not recommendations:
            return {
                'candidate_id': str(candidate_id),
                'total_recommendations': 0,
                'recommendations': [],
                'message': 'No job matches found for this candidate.'
            }

        # Get job details
        job_ids = [rec.job_id for rec in recommendations]
        stmt = select(Job).where(Job.id.in_(job_ids))
        result = await db.execute(stmt)
        jobs = {j.id: j for j in result.scalars().all()}

        # Build response
        recommendations_list = []
        for rec in recommendations:
            job = jobs.get(rec.job_id)
            if job:
                rec_dict = {
                    'rank': rec.rank,
                    'match_score': float(rec.match_score),
                    'job': {
                        'id': str(job.id),
                        'title': job.title,
                        'department': job.department,
                        'location': job.location,
                        'employment_type': job.employment_type,
                        'work_mode': job.work_mode,
                        'salary_min': job.salary_min,
                        'salary_max': job.salary_max,
                        'experience_min': job.experience_min,
                        'experience_max': job.experience_max,
                        'status': job.status,
                    },
                    'match_details': rec.match_details,
                    'created_at': rec.created_at.isoformat() if rec.created_at else None
                }
                recommendations_list.append(rec_dict)

        return {
            'candidate_id': str(candidate_id),
            'candidate_name': f"{candidate.first_name} {candidate.last_name}",
            'total_recommendations': len(recommendations_list),
            'recommendations': recommendations_list
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting candidate recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting recommendations: {str(e)}"
        )
