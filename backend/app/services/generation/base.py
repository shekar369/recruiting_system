"""
Abstract base class for LLM generation providers
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, AsyncIterator, Any
from pydantic import BaseModel


class Message(BaseModel):
    """Chat message model"""
    role: str  # 'system', 'user', 'assistant'
    content: str


class GenerationConfig(BaseModel):
    """Configuration for text generation"""
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    stop: Optional[List[str]] = None
    stream: bool = False


class GenerationResponse(BaseModel):
    """Response from generation"""
    content: str
    model: str
    usage: Optional[Dict[str, int]] = None
    finish_reason: Optional[str] = None


class GenerationProvider(ABC):
    """Abstract base class for LLM providers"""

    def __init__(self, model_name: str, **kwargs):
        """
        Initialize the provider

        Args:
            model_name: Name of the model to use
            **kwargs: Additional provider-specific configuration
        """
        self.model_name = model_name
        self.config = kwargs

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None
    ) -> GenerationResponse:
        """
        Generate text from a prompt

        Args:
            prompt: Input prompt text
            config: Generation configuration

        Returns:
            GenerationResponse with generated text
        """
        pass

    @abstractmethod
    async def chat(
        self,
        messages: List[Message],
        config: Optional[GenerationConfig] = None
    ) -> GenerationResponse:
        """
        Generate chat completion from messages

        Args:
            messages: List of chat messages
            config: Generation configuration

        Returns:
            GenerationResponse with assistant message
        """
        pass

    @abstractmethod
    async def stream(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None
    ) -> AsyncIterator[str]:
        """
        Stream generated text tokens

        Args:
            prompt: Input prompt text
            config: Generation configuration

        Yields:
            Generated text chunks
        """
        pass

    @abstractmethod
    async def chat_stream(
        self,
        messages: List[Message],
        config: Optional[GenerationConfig] = None
    ) -> AsyncIterator[str]:
        """
        Stream chat completion tokens

        Args:
            messages: List of chat messages
            config: Generation configuration

        Yields:
            Generated text chunks
        """
        pass

    def get_model_info(self) -> Dict[str, Any]:
        """Get provider and model information"""
        return {
            'provider': self.__class__.__name__,
            'model': self.model_name,
            'config': self.config
        }
