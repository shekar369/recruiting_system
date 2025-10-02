"""
Matching Service for intelligent job-candidate matching
"""
import logging
from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import numpy as np

from app.models.job import Job, JobRecommendation
from app.models.candidate import Candidate
from app.services.search_service import search_service

logger = logging.getLogger(__name__)


class Match:
    """Job-candidate match with detailed scoring"""
    def __init__(self, job_id: UUID, candidate_id: UUID):
        self.job_id = job_id
        self.candidate_id = candidate_id
        self.semantic_score = 0.0
        self.skills_score = 0.0
        self.experience_score = 0.0
        self.location_score = 0.0
        self.overall_score = 0.0
        self.explanation = ""
        self.matching_skills = []
        self.missing_skills = []

    def calculate_overall_score(self):
        """Calculate weighted overall match score"""
        self.overall_score = (
            0.40 * self.semantic_score +
            0.30 * self.skills_score +
            0.20 * self.experience_score +
            0.10 * self.location_score
        )

    def to_dict(self):
        return {
            'job_id': str(self.job_id),
            'candidate_id': str(self.candidate_id),
            'overall_score': float(self.overall_score),
            'score_breakdown': {
                'semantic_similarity': float(self.semantic_score),
                'skills_match': float(self.skills_score),
                'experience_match': float(self.experience_score),
                'location_match': float(self.location_score)
            },
            'matching_skills': self.matching_skills,
            'missing_skills': self.missing_skills,
            'explanation': self.explanation
        }


class MatchingService:
    """Service for job-candidate matching"""

    def __init__(self):
        pass

    def calculate_skill_match(
        self,
        job_skills: List[str],
        candidate_skills: List[str]
    ) -> tuple[float, List[str], List[str]]:
        """
        Calculate skill match percentage

        Args:
            job_skills: Required and preferred skills from job
            candidate_skills: Candidate's skills

        Returns:
            Tuple of (match_percentage, matching_skills, missing_skills)
        """
        if not job_skills:
            return 1.0, [], []

        # Normalize skills to lowercase for comparison
        job_skills_lower = [s.lower() for s in job_skills]
        candidate_skills_lower = [s.lower() for s in candidate_skills]

        # Find matches
        matching = [s for s in job_skills if s.lower() in candidate_skills_lower]
        missing = [s for s in job_skills if s.lower() not in candidate_skills_lower]

        # Calculate percentage
        match_percentage = len(matching) / len(job_skills) if job_skills else 0

        return match_percentage, matching, missing

    def calculate_experience_match(
        self,
        required_min: Optional[int],
        required_max: Optional[int],
        candidate_experience: Optional[int]
    ) -> float:
        """
        Calculate experience match score

        Args:
            required_min: Minimum required experience years
            required_max: Maximum required experience years
            candidate_experience: Candidate's years of experience

        Returns:
            Match score (0.0 to 1.0)
        """
        if candidate_experience is None:
            return 0.5  # Unknown experience

        if required_min is None and required_max is None:
            return 1.0  # No experience requirement

        # Check if within range
        if required_min is not None and candidate_experience < required_min:
            # Below minimum: penalize based on gap
            gap = required_min - candidate_experience
            if gap <= 1:
                return 0.8
            elif gap <= 2:
                return 0.6
            else:
                return 0.3

        if required_max is not None and candidate_experience > required_max:
            # Above maximum: slight penalty (overqualified)
            gap = candidate_experience - required_max
            if gap <= 2:
                return 0.9
            elif gap <= 5:
                return 0.7
            else:
                return 0.5

        # Within range
        return 1.0

    def calculate_location_match(
        self,
        job_location: Optional[str],
        candidate_location: Optional[str],
        job_work_mode: Optional[str]
    ) -> float:
        """
        Calculate location match score

        Args:
            job_location: Job location
            candidate_location: Candidate location
            job_work_mode: remote, hybrid, or onsite

        Returns:
            Match score (0.0 to 1.0)
        """
        # Remote jobs always match
        if job_work_mode and job_work_mode.lower() == 'remote':
            return 1.0

        if not job_location or not candidate_location:
            return 0.5  # Unknown location

        # Normalize locations
        job_loc_lower = job_location.lower()
        cand_loc_lower = candidate_location.lower()

        # Exact match
        if job_loc_lower == cand_loc_lower:
            return 1.0

        # Partial match (same city or state)
        job_parts = job_loc_lower.split(',')
        cand_parts = cand_loc_lower.split(',')

        # Check if any part matches
        for job_part in job_parts:
            for cand_part in cand_parts:
                if job_part.strip() in cand_part.strip() or cand_part.strip() in job_part.strip():
                    return 0.7

        # Hybrid mode - nearby might work
        if job_work_mode and job_work_mode.lower() == 'hybrid':
            return 0.4

        # No match for onsite
        return 0.2

    def generate_match_explanation(self, match: Match) -> str:
        """
        Generate human-readable match explanation

        Args:
            match: Match object with calculated scores

        Returns:
            Explanation string
        """
        explanations = []

        # Overall assessment
        if match.overall_score >= 0.8:
            explanations.append("Excellent match!")
        elif match.overall_score >= 0.6:
            explanations.append("Good match.")
        elif match.overall_score >= 0.4:
            explanations.append("Moderate match.")
        else:
            explanations.append("Weak match.")

        # Skills
        if match.skills_score >= 0.8:
            explanations.append(f"Strong skills alignment ({len(match.matching_skills)}/{len(match.matching_skills) + len(match.missing_skills)} required skills).")
        elif match.skills_score >= 0.5:
            explanations.append(f"Partial skills match ({len(match.matching_skills)}/{len(match.matching_skills) + len(match.missing_skills)} required skills).")
        else:
            explanations.append(f"Limited skills overlap ({len(match.matching_skills)}/{len(match.matching_skills) + len(match.missing_skills)} required skills).")

        # Experience
        if match.experience_score >= 0.9:
            explanations.append("Experience level is ideal.")
        elif match.experience_score >= 0.7:
            explanations.append("Experience level is acceptable.")
        elif match.experience_score < 0.5:
            explanations.append("Experience level may not meet requirements.")

        # Location
        if match.location_score >= 0.9:
            explanations.append("Location is a perfect match.")
        elif match.location_score < 0.5:
            explanations.append("Location may be a concern.")

        return " ".join(explanations)

    async def match_candidates_to_job(
        self,
        db: AsyncSession,
        job_id: UUID,
        top_k: int = 20
    ) -> List[Match]:
        """
        Find and rank candidate matches for a job

        Args:
            db: Database session
            job_id: Job ID to match candidates for
            top_k: Number of top matches to return

        Returns:
            List of Match objects, ranked by overall score
        """
        try:
            # Step 1: Get job details
            stmt = select(Job).where(Job.id == job_id)
            result = await db.execute(stmt)
            job = result.scalar_one_or_none()

            if not job:
                raise ValueError(f"Job {job_id} not found")

            logger.info(f"Matching candidates for job: {job.title}")

            # Step 2: Prepare search query from job description
            search_query = f"{job.title}. {job.description or ''}"

            # Step 3: Prepare filters
            filters = {
                'status': 'active'
            }

            if job.experience_min:
                filters['experience_min'] = job.experience_min

            # Step 4: Perform hybrid search
            search_results = await search_service.hybrid_search(
                db=db,
                query=search_query,
                filters=filters,
                top_k=top_k * 2  # Get more for filtering
            )

            # Step 5: Calculate detailed match scores
            matches = []
            all_job_skills = (job.required_skills or []) + (job.preferred_skills or [])

            for search_result in search_results:
                candidate = search_result.candidate

                # Get candidate skills from parsed resume data
                candidate_stmt = select(Candidate).where(Candidate.id == candidate.id)
                cand_result = await db.execute(candidate_stmt)
                full_candidate = cand_result.scalar_one()

                # Extract skills from resume if available
                candidate_skills = []
                if hasattr(full_candidate, 'resumes') and full_candidate.resumes:
                    for resume in full_candidate.resumes:
                        if resume.parsed_data and 'skills' in resume.parsed_data:
                            candidate_skills.extend(resume.parsed_data['skills'])

                # Create match object
                match = Match(job_id=job_id, candidate_id=candidate.id)

                # Semantic score (from search)
                match.semantic_score = search_result.score

                # Skills match
                skills_match, matching, missing = self.calculate_skill_match(
                    all_job_skills,
                    candidate_skills
                )
                match.skills_score = skills_match
                match.matching_skills = matching
                match.missing_skills = missing

                # Experience match
                match.experience_score = self.calculate_experience_match(
                    job.experience_min,
                    job.experience_max,
                    candidate.years_of_experience
                )

                # Location match
                match.location_score = self.calculate_location_match(
                    job.location,
                    candidate.location,
                    job.work_mode
                )

                # Calculate overall score
                match.calculate_overall_score()

                # Generate explanation
                match.explanation = self.generate_match_explanation(match)

                matches.append(match)

            # Step 6: Sort by overall score
            matches.sort(key=lambda m: m.overall_score, reverse=True)

            logger.info(f"Generated {len(matches[:top_k])} matches for job {job_id}")
            return matches[:top_k]

        except Exception as e:
            logger.error(f"Error matching candidates to job: {e}")
            raise

    async def save_recommendations(
        self,
        db: AsyncSession,
        job_id: UUID,
        matches: List[Match]
    ) -> None:
        """
        Save match recommendations to database

        Args:
            db: Database session
            job_id: Job ID
            matches: List of Match objects
        """
        try:
            # Delete existing recommendations for this job
            from sqlalchemy import delete
            stmt = delete(JobRecommendation).where(JobRecommendation.job_id == job_id)
            await db.execute(stmt)

            # Create new recommendations
            for rank, match in enumerate(matches, 1):
                recommendation = JobRecommendation(
                    job_id=job_id,
                    candidate_id=match.candidate_id,
                    match_score=match.overall_score,
                    rank=rank,
                    match_details={
                        'semantic_score': match.semantic_score,
                        'skills_score': match.skills_score,
                        'experience_score': match.experience_score,
                        'location_score': match.location_score,
                        'matching_skills': match.matching_skills,
                        'missing_skills': match.missing_skills,
                        'explanation': match.explanation
                    }
                )
                db.add(recommendation)

            await db.commit()
            logger.info(f"Saved {len(matches)} recommendations for job {job_id}")

        except Exception as e:
            await db.rollback()
            logger.error(f"Error saving recommendations: {e}")
            raise


# Singleton instance
matching_service = MatchingService()
