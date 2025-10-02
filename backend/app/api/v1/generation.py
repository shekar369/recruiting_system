"""
Generation endpoints for LLM-powered features
"""
import logging
from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.services.generation import get_generation_service, Message

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/generation", tags=["generation"])


class SummarizeResumeRequest(BaseModel):
    """Request to summarize a resume"""
    resume_id: UUID
    max_length: int = 200


class GenerateJobDescriptionRequest(BaseModel):
    """Request to generate job description"""
    job_id: UUID
    tone: str = "professional"


class GenerateInterviewQuestionsRequest(BaseModel):
    """Request to generate interview questions"""
    job_id: UUID
    candidate_id: UUID
    num_questions: int = 10


class GenerateEmailRequest(BaseModel):
    """Request to generate email"""
    template_type: str  # rejection, invitation, offer, follow_up
    context: dict
    tone: str = "professional"


class ChatRequest(BaseModel):
    """Chat request"""
    messages: List[dict]
    temperature: float = 0.7
    max_tokens: Optional[int] = None


@router.post("/summarize-resume")
async def summarize_resume(
    request: SummarizeResumeRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a concise summary of a resume

    Args:
        request: Summarize request
        db: Database session

    Returns:
        Resume summary
    """
    try:
        generation_service = get_generation_service()

        summary = await generation_service.summarize_resume(
            db=db,
            resume_id=request.resume_id,
            max_length=request.max_length
        )

        return {
            'resume_id': str(request.resume_id),
            'summary': summary,
            'max_length': request.max_length
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error summarizing resume: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error summarizing resume: {str(e)}"
        )


@router.post("/generate-job-description")
async def generate_job_description(
    request: GenerateJobDescriptionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate or enhance a job description

    Args:
        request: Generate job description request
        db: Database session

    Returns:
        Generated job description
    """
    try:
        generation_service = get_generation_service()

        description = await generation_service.generate_job_description(
            db=db,
            job_id=request.job_id,
            tone=request.tone
        )

        return {
            'job_id': str(request.job_id),
            'description': description,
            'tone': request.tone
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error generating job description: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating job description: {str(e)}"
        )


@router.post("/generate-interview-questions")
async def generate_interview_questions(
    request: GenerateInterviewQuestionsRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate tailored interview questions

    Args:
        request: Generate interview questions request
        db: Database session

    Returns:
        List of interview questions
    """
    try:
        generation_service = get_generation_service()

        questions = await generation_service.generate_interview_questions(
            db=db,
            job_id=request.job_id,
            candidate_id=request.candidate_id,
            num_questions=request.num_questions
        )

        return {
            'job_id': str(request.job_id),
            'candidate_id': str(request.candidate_id),
            'total_questions': len(questions),
            'questions': questions
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error generating interview questions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating interview questions: {str(e)}"
        )


@router.post("/generate-email")
async def generate_email(request: GenerateEmailRequest):
    """
    Generate recruitment emails

    Args:
        request: Generate email request

    Returns:
        Generated email with subject and body
    """
    try:
        generation_service = get_generation_service()

        email = await generation_service.generate_email(
            template_type=request.template_type,
            context=request.context,
            tone=request.tone
        )

        return {
            'template_type': request.template_type,
            'tone': request.tone,
            'subject': email['subject'],
            'body': email['body']
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error generating email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating email: {str(e)}"
        )


@router.post("/chat")
async def chat(request: ChatRequest):
    """
    Generic chat interface

    Args:
        request: Chat request with messages

    Returns:
        Assistant response
    """
    try:
        from app.services.generation.base import GenerationConfig

        generation_service = get_generation_service()

        # Convert dict messages to Message objects
        messages = [
            Message(role=msg['role'], content=msg['content'])
            for msg in request.messages
        ]

        config = GenerationConfig(
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )

        response = await generation_service.chat(messages, config)

        return {
            'response': response,
            'provider': generation_service.get_provider_info()
        }

    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in chat: {str(e)}"
        )


@router.get("/provider-info")
async def get_provider_info():
    """
    Get current LLM provider information

    Returns:
        Provider details
    """
    try:
        generation_service = get_generation_service()
        return generation_service.get_provider_info()

    except Exception as e:
        logger.error(f"Error getting provider info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting provider info: {str(e)}"
        )
