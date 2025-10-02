"""
Search Service for hybrid candidate search
Combines PostgreSQL filtering with FAISS semantic search
"""
import logging
from typing import List, Dict, Optional, Any
from uuid import UUID
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
import numpy as np

from app.models.candidate import Candidate, CandidateSkill
from app.services.embedding_service import get_embedding_service
from app.services.vector_service import get_vector_service

logger = logging.getLogger(__name__)


class SearchResult:
    """Search result with candidate and score"""
    def __init__(self, candidate: Candidate, score: float, chunks: List[Dict] = None):
        self.candidate = candidate
        self.score = score
        self.chunks = chunks or []
        self.match_details = {}

    def to_dict(self):
        return {
            'candidate': {
                'id': self.candidate.id,
                'first_name': self.candidate.first_name,
                'last_name': self.candidate.last_name,
                'email': self.candidate.email,
                'phone': self.candidate.phone,
                'location': self.candidate.location,
                'current_job_title': self.candidate.current_job_title,
                'current_company': self.candidate.current_company,
                'years_of_experience': self.candidate.years_of_experience,
                'status': self.candidate.status,
            },
            'score': float(self.score),
            'match_details': self.match_details,
            'matching_chunks': [
                {
                    'chunk_text': chunk.get('chunk_text', '')[:200] + '...' if len(chunk.get('chunk_text', '')) > 200 else chunk.get('chunk_text', ''),
                    'chunk_type': chunk.get('chunk_type'),
                    'score': chunk.get('score')
                }
                for chunk in self.chunks[:3]  # Top 3 matching chunks
            ]
        }


class SearchService:
    """Service for hybrid candidate search"""

    def __init__(self):
        self.embedding_service = None
        self.vector_service = None

    def _get_services(self):
        """Lazy load services"""
        if self.embedding_service is None:
            self.embedding_service = get_embedding_service()
        if self.vector_service is None:
            self.vector_service = get_vector_service()
        return self.embedding_service, self.vector_service

    async def structured_filter(
        self,
        db: AsyncSession,
        filters: Dict[str, Any]
    ) -> List[UUID]:
        """
        Filter candidates using PostgreSQL queries

        Args:
            db: Database session
            filters: Filter criteria
                - location: str (partial match)
                - experience_min: int
                - experience_max: int
                - salary_min: float
                - salary_max: float
                - skills: List[str] (any match)
                - status: str

        Returns:
            List of candidate UUIDs matching filters
        """
        try:
            # Build query conditions
            conditions = []

            # Location filter (case-insensitive partial match)
            if filters.get('location'):
                conditions.append(
                    Candidate.location.ilike(f"%{filters['location']}%")
                )

            # Experience range
            if filters.get('experience_min') is not None:
                conditions.append(
                    Candidate.years_of_experience >= filters['experience_min']
                )
            if filters.get('experience_max') is not None:
                conditions.append(
                    Candidate.years_of_experience <= filters['experience_max']
                )

            # Salary range
            if filters.get('salary_min') is not None:
                conditions.append(
                    Candidate.expected_salary_min >= filters['salary_min']
                )
            if filters.get('salary_max') is not None:
                conditions.append(
                    Candidate.expected_salary_max <= filters['salary_max']
                )

            # Status filter
            if filters.get('status'):
                conditions.append(Candidate.status == filters['status'])
            else:
                # Default to active candidates
                conditions.append(Candidate.status == 'active')

            # Skills filter - requires join with candidate_skills
            skills = filters.get('skills', [])
            if skills:
                # Build query with skills join
                stmt = select(Candidate.id).join(
                    CandidateSkill,
                    Candidate.id == CandidateSkill.candidate_id
                ).where(
                    and_(
                        *conditions,
                        CandidateSkill.skill_name.in_(skills)
                    )
                ).distinct()
            else:
                # Query without skills filter
                stmt = select(Candidate.id).where(and_(*conditions))

            result = await db.execute(stmt)
            candidate_ids = [row[0] for row in result.all()]

            logger.info(f"Structured filter found {len(candidate_ids)} candidates")
            return candidate_ids

        except Exception as e:
            logger.error(f"Error in structured filter: {e}")
            raise

    async def semantic_search(
        self,
        query: str,
        candidate_pool: Optional[List[UUID]] = None,
        top_k: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search using FAISS

        Args:
            query: Search query text
            candidate_pool: Optional list of candidate IDs to filter by
            top_k: Number of results to return

        Returns:
            List of matches with candidate_id, score, and chunk info
        """
        try:
            embedding_service, vector_service = self._get_services()

            # Generate query embedding
            query_embedding = embedding_service.embed_text(query)

            # Search FAISS index
            results = vector_service.search(
                query_vector=query_embedding,
                k=top_k,
                candidate_id_filter=candidate_pool
            )

            logger.info(f"Semantic search found {len(results)} matches")
            return results

        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            raise

    async def aggregate_by_candidate(
        self,
        chunk_matches: List[Dict[str, Any]]
    ) -> Dict[UUID, Dict[str, Any]]:
        """
        Aggregate chunk-level matches to candidate-level scores

        Args:
            chunk_matches: List of chunk matches from FAISS

        Returns:
            Dict mapping candidate_id to aggregated score and chunks
        """
        candidate_aggregates = {}

        for match in chunk_matches:
            candidate_id = UUID(match['candidate_id'])

            if candidate_id not in candidate_aggregates:
                candidate_aggregates[candidate_id] = {
                    'chunks': [],
                    'scores': [],
                    'max_score': 0,
                    'avg_score': 0
                }

            agg = candidate_aggregates[candidate_id]
            agg['chunks'].append(match)
            agg['scores'].append(match['score'])
            agg['max_score'] = max(agg['max_score'], match['score'])

        # Calculate average scores
        for candidate_id, agg in candidate_aggregates.items():
            agg['avg_score'] = np.mean(agg['scores'])
            # Use weighted score: 70% max, 30% average
            agg['final_score'] = 0.7 * agg['max_score'] + 0.3 * agg['avg_score']

        return candidate_aggregates

    async def hybrid_search(
        self,
        db: AsyncSession,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 20
    ) -> List[SearchResult]:
        """
        Perform hybrid search combining structured filters and semantic search

        Args:
            db: Database session
            query: Search query text
            filters: Optional filter criteria
            top_k: Number of results to return

        Returns:
            List of SearchResult objects, ranked by score
        """
        try:
            # Step 1: Apply structured filters if provided
            candidate_pool = None
            if filters:
                candidate_pool = await self.structured_filter(db, filters)
                if not candidate_pool:
                    logger.info("No candidates match the structured filters")
                    return []

            # Step 2: Perform semantic search
            chunk_matches = await self.semantic_search(
                query=query,
                candidate_pool=candidate_pool,
                top_k=100  # Get more chunks, then aggregate
            )

            if not chunk_matches:
                logger.info("No semantic matches found")
                return []

            # Step 3: Aggregate by candidate
            candidate_aggregates = await self.aggregate_by_candidate(chunk_matches)

            # Step 4: Get candidate details from database
            candidate_ids = list(candidate_aggregates.keys())
            stmt = select(Candidate).where(Candidate.id.in_(candidate_ids))
            result = await db.execute(stmt)
            candidates = {c.id: c for c in result.scalars().all()}

            # Step 5: Create SearchResult objects
            search_results = []
            for candidate_id, agg in candidate_aggregates.items():
                if candidate_id in candidates:
                    search_result = SearchResult(
                        candidate=candidates[candidate_id],
                        score=agg['final_score'],
                        chunks=agg['chunks']
                    )
                    search_result.match_details = {
                        'max_chunk_score': agg['max_score'],
                        'avg_chunk_score': agg['avg_score'],
                        'num_matching_chunks': len(agg['chunks'])
                    }
                    search_results.append(search_result)

            # Step 6: Sort by score (descending)
            search_results.sort(key=lambda x: x.score, reverse=True)

            # Step 7: Return top_k results
            logger.info(f"Hybrid search returned {len(search_results[:top_k])} candidates")
            return search_results[:top_k]

        except Exception as e:
            logger.error(f"Error in hybrid search: {e}")
            raise


# Singleton instance
search_service = SearchService()
