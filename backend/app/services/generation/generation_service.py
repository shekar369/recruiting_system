"""
Generation Service with prompt templates and use cases
"""
import logging
from typing import Dict, Optional, List, Any
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.candidate import Candidate, CandidateResume
from app.models.job import Job
from .base import GenerationProvider, GenerationConfig, Message
from .ollama_provider import OllamaProvider
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider

logger = logging.getLogger(__name__)


class GenerationService:
    """Service for LLM-powered text generation"""

    def __init__(self, provider: str = "ollama", **provider_kwargs):
        """
        Initialize generation service

        Args:
            provider: Provider name ('ollama', 'openai', 'anthropic')
            **provider_kwargs: Provider-specific configuration
        """
        self.provider = self._create_provider(provider, **provider_kwargs)

    def _create_provider(self, provider_name: str, **kwargs) -> GenerationProvider:
        """Create provider instance"""
        providers = {
            'ollama': OllamaProvider,
            'openai': OpenAIProvider,
            'anthropic': AnthropicProvider
        }

        provider_class = providers.get(provider_name.lower())
        if not provider_class:
            raise ValueError(f"Unknown provider: {provider_name}")

        return provider_class(**kwargs)

    async def summarize_resume(
        self,
        db: AsyncSession,
        resume_id: UUID,
        max_length: int = 200
    ) -> str:
        """
        Generate a concise summary of a resume

        Args:
            db: Database session
            resume_id: Resume ID
            max_length: Maximum summary length in words

        Returns:
            Resume summary text
        """
        # Fetch resume
        stmt = select(CandidateResume).where(CandidateResume.id == resume_id)
        result = await db.execute(stmt)
        resume = result.scalar_one_or_none()

        if not resume:
            raise ValueError(f"Resume {resume_id} not found")

        # Build prompt
        parsed_data = resume.parsed_data or {}

        prompt = f"""Summarize this resume in {max_length} words or less. Focus on key qualifications, experience, and skills.

Resume Details:
- Skills: {', '.join(parsed_data.get('skills', []))}
- Education: {', '.join([f"{e.get('degree', '')} in {e.get('field', '')} from {e.get('institution', '')}" for e in parsed_data.get('education', [])])}
- Experience: {', '.join([f"{exp.get('title', '')} at {exp.get('company', '')}" for exp in parsed_data.get('experience', [])])}

Full Text:
{resume.raw_text[:3000] if resume.raw_text else 'No text available'}

Summary:"""

        config = GenerationConfig(
            temperature=0.3,
            max_tokens=max_length * 2  # Rough tokens estimate
        )

        response = await self.provider.generate(prompt, config)
        return response.content.strip()

    async def generate_job_description(
        self,
        db: AsyncSession,
        job_id: UUID,
        tone: str = "professional"
    ) -> str:
        """
        Generate or enhance a job description

        Args:
            db: Database session
            job_id: Job ID
            tone: Tone of the description (professional, casual, exciting)

        Returns:
            Generated job description
        """
        # Fetch job
        stmt = select(Job).where(Job.id == job_id)
        result = await db.execute(stmt)
        job = result.scalar_one_or_none()

        if not job:
            raise ValueError(f"Job {job_id} not found")

        # Build prompt
        prompt = f"""Write a compelling job description with a {tone} tone.

Job Details:
- Title: {job.title}
- Department: {job.department}
- Location: {job.location}
- Work Mode: {job.work_mode}
- Experience Required: {job.experience_min}-{job.experience_max} years
- Required Skills: {', '.join(job.required_skills or [])}
- Preferred Skills: {', '.join(job.preferred_skills or [])}
- Salary Range: ${job.salary_min:,} - ${job.salary_max:,}

Current Description:
{job.description or 'None provided'}

Generate a structured job description with:
1. Company overview
2. Role summary
3. Key responsibilities
4. Required qualifications
5. Preferred qualifications
6. Benefits and perks

Job Description:"""

        config = GenerationConfig(
            temperature=0.7,
            max_tokens=800
        )

        response = await self.provider.generate(prompt, config)
        return response.content.strip()

    async def generate_interview_questions(
        self,
        db: AsyncSession,
        job_id: UUID,
        candidate_id: UUID,
        num_questions: int = 10
    ) -> List[Dict[str, str]]:
        """
        Generate tailored interview questions

        Args:
            db: Database session
            job_id: Job ID
            candidate_id: Candidate ID
            num_questions: Number of questions to generate

        Returns:
            List of question dictionaries with category and text
        """
        # Fetch job and candidate
        job_stmt = select(Job).where(Job.id == job_id)
        cand_stmt = select(Candidate).where(Candidate.id == candidate_id)

        job_result = await db.execute(job_stmt)
        cand_result = await db.execute(cand_stmt)

        job = job_result.scalar_one_or_none()
        candidate = cand_result.scalar_one_or_none()

        if not job or not candidate:
            raise ValueError("Job or candidate not found")

        # Build prompt
        prompt = f"""Generate {num_questions} tailored interview questions for this candidate-job pairing.

Job: {job.title}
Required Skills: {', '.join(job.required_skills or [])}
Experience Level: {job.experience_min}-{job.experience_max} years

Candidate: {candidate.first_name} {candidate.last_name}
Current Role: {candidate.current_job_title or 'N/A'}
Experience: {candidate.years_of_experience} years

Generate questions in these categories:
- Technical (3-4 questions)
- Behavioral (3-4 questions)
- Situational (2-3 questions)

Format each question as:
[CATEGORY] Question text here

Questions:"""

        config = GenerationConfig(
            temperature=0.8,
            max_tokens=1000
        )

        response = await self.provider.generate(prompt, config)

        # Parse response into structured format
        questions = []
        for line in response.content.strip().split('\n'):
            line = line.strip()
            if line and '[' in line and ']' in line:
                category = line[line.index('[')+1:line.index(']')]
                question_text = line[line.index(']')+1:].strip()
                questions.append({
                    'category': category,
                    'question': question_text
                })

        return questions[:num_questions]

    async def generate_email(
        self,
        template_type: str,
        context: Dict[str, Any],
        tone: str = "professional"
    ) -> Dict[str, str]:
        """
        Generate recruitment emails

        Args:
            template_type: Type of email (rejection, invitation, offer, follow_up)
            context: Context data for email generation
            tone: Email tone (professional, friendly, formal)

        Returns:
            Dictionary with subject and body
        """
        templates = {
            'rejection': """Write a {tone} rejection email.

Candidate: {candidate_name}
Position: {job_title}

Include:
- Thank them for their interest
- Inform them they were not selected
- Encourage future applications
- Keep it brief and respectful

Email:""",

            'invitation': """Write a {tone} interview invitation email.

Candidate: {candidate_name}
Position: {job_title}
Interview Type: {interview_type}
Date/Time: {interview_datetime}
Location/Link: {location}

Include:
- Congratulate them on being selected
- Provide interview details
- What to prepare/bring
- Contact information for questions

Email:""",

            'offer': """Write a {tone} job offer email.

Candidate: {candidate_name}
Position: {job_title}
Salary: {salary}
Start Date: {start_date}

Include:
- Congratulations on the offer
- Position details
- Compensation and benefits
- Next steps
- Response deadline

Email:""",

            'follow_up': """Write a {tone} follow-up email.

Candidate: {candidate_name}
Position: {job_title}
Last Contact: {last_contact}
Status: {status}

Include:
- Reference to previous interaction
- Current status update
- Next steps
- Timeline

Email:"""
        }

        template = templates.get(template_type)
        if not template:
            raise ValueError(f"Unknown template type: {template_type}")

        # Build prompt
        prompt = template.format(tone=tone, **context)

        config = GenerationConfig(
            temperature=0.7,
            max_tokens=500
        )

        response = await self.provider.generate(prompt, config)

        # Parse subject and body
        content = response.content.strip()

        # Try to extract subject line
        subject = f"Regarding {context.get('job_title', 'Your Application')}"
        body = content

        if 'Subject:' in content:
            parts = content.split('Subject:', 1)
            if len(parts) == 2:
                subject_line = parts[1].split('\n', 1)
                subject = subject_line[0].strip()
                body = subject_line[1].strip() if len(subject_line) > 1 else parts[0].strip()

        return {
            'subject': subject,
            'body': body
        }

    async def chat(
        self,
        messages: List[Message],
        config: Optional[GenerationConfig] = None
    ) -> str:
        """
        Generic chat interface

        Args:
            messages: List of chat messages
            config: Generation configuration

        Returns:
            Assistant response text
        """
        response = await self.provider.chat(messages, config)
        return response.content

    def get_provider_info(self) -> Dict[str, Any]:
        """Get current provider information"""
        return self.provider.get_model_info()


# Singleton instance
_generation_service_instance: Optional[GenerationService] = None


def get_generation_service(
    provider: Optional[str] = None,
    **provider_kwargs
) -> GenerationService:
    """
    Get or create generation service singleton

    Args:
        provider: Provider name (ollama, openai, anthropic)
        **provider_kwargs: Provider-specific configuration

    Returns:
        GenerationService instance
    """
    global _generation_service_instance

    # Use provider from settings if not specified
    provider = provider or getattr(settings, 'LLM_PROVIDER', 'ollama')

    if _generation_service_instance is None:
        _generation_service_instance = GenerationService(
            provider=provider,
            **provider_kwargs
        )

    return _generation_service_instance
