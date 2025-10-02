"""
Search endpoints for candidate search
"""
import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.services.search_service import search_service
from app.services.reranking_service import get_reranking_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["search"])


class SearchFilters(BaseModel):
    """Search filter criteria"""
    location: Optional[str] = None
    experience_min: Optional[int] = None
    experience_max: Optional[int] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    skills: Optional[List[str]] = None
    status: Optional[str] = 'active'


class SearchRequest(BaseModel):
    """Search request model"""
    query: str
    filters: Optional[SearchFilters] = None
    top_k: int = 20
    use_reranking: bool = False


@router.post("/candidates")
async def search_candidates(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Search for candidates using hybrid search

    Args:
        request: Search request with query and filters
        db: Database session

    Returns:
        Paginated search results with scores
    """
    try:
        # Convert filters to dict
        filters_dict = request.filters.dict() if request.filters else {}

        # Perform hybrid search
        search_results = await search_service.hybrid_search(
            db=db,
            query=request.query,
            filters=filters_dict,
            top_k=request.top_k * 2 if request.use_reranking else request.top_k
        )

        # Apply reranking if requested
        if request.use_reranking and search_results:
            try:
                reranking_service = get_reranking_service()

                # Extract candidate summaries for reranking
                def extract_document(result):
                    c = result.candidate
                    return f"{c.first_name} {c.last_name}. {c.current_job_title or ''} at {c.current_company or ''}. Location: {c.location or 'Unknown'}. Experience: {c.years_of_experience or 0} years."

                search_results = reranking_service.rerank_search_results(
                    query=request.query,
                    search_results=search_results,
                    document_extractor=extract_document,
                    top_k=request.top_k
                )
            except Exception as e:
                logger.warning(f"Reranking failed, using original results: {e}")

        # Convert to dict
        results = [result.to_dict() for result in search_results[:request.top_k]]

        # Add reranking metadata if used
        for result in results:
            if request.use_reranking and hasattr(result, 'rerank_score'):
                result['rerank_score'] = result.get('rerank_score')
                result['rank_change'] = result.get('rank_change')

        return {
            'query': request.query,
            'total_results': len(results),
            'filters_applied': filters_dict,
            'reranking_used': request.use_reranking,
            'results': results
        }

    except Exception as e:
        logger.error(f"Error in candidate search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching candidates: {str(e)}"
        )


@router.post("/candidates/compare")
async def compare_search_methods(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    A/B test comparing search results with and without reranking

    Args:
        request: Search request
        db: Database session

    Returns:
        Comparison of results with and without reranking
    """
    try:
        # Convert filters to dict
        filters_dict = request.filters.dict() if request.filters else {}

        # Perform hybrid search
        base_results = await search_service.hybrid_search(
            db=db,
            query=request.query,
            filters=filters_dict,
            top_k=request.top_k
        )

        # Get results without reranking
        without_reranking = [result.to_dict() for result in base_results]

        # Get results with reranking
        with_reranking = []
        if base_results:
            try:
                reranking_service = get_reranking_service()

                def extract_document(result):
                    c = result.candidate
                    return f"{c.first_name} {c.last_name}. {c.current_job_title or ''} at {c.current_company or ''}. Location: {c.location or 'Unknown'}. Experience: {c.years_of_experience or 0} years."

                reranked_results = reranking_service.rerank_search_results(
                    query=request.query,
                    search_results=base_results.copy(),
                    document_extractor=extract_document,
                    top_k=request.top_k
                )

                with_reranking = [result.to_dict() for result in reranked_results]

            except Exception as e:
                logger.error(f"Reranking failed in comparison: {e}")
                with_reranking = without_reranking

        return {
            'query': request.query,
            'filters_applied': filters_dict,
            'without_reranking': {
                'total': len(without_reranking),
                'results': without_reranking[:5]  # Top 5 for comparison
            },
            'with_reranking': {
                'total': len(with_reranking),
                'results': with_reranking[:5]  # Top 5 for comparison
            },
            'analysis': {
                'ranking_changes': sum(1 for i, r in enumerate(with_reranking[:5]) if r.get('rank_change', 0) != 0),
                'avg_score_without': sum(r['score'] for r in without_reranking[:5]) / min(5, len(without_reranking)) if without_reranking else 0,
                'avg_rerank_score': sum(r.get('rerank_score', 0) for r in with_reranking[:5]) / min(5, len(with_reranking)) if with_reranking else 0
            }
        }

    except Exception as e:
        logger.error(f"Error in search comparison: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error comparing search methods: {str(e)}"
        )
