"""
OpenAI provider for GPT models
"""
import logging
from typing import List, Optional, AsyncIterator
from openai import AsyncOpenAI
from .base import GenerationProvider, GenerationConfig, GenerationResponse, Message

logger = logging.getLogger(__name__)


class OpenAIProvider(GenerationProvider):
    """OpenAI provider for GPT models"""

    def __init__(
        self,
        model_name: str = "gpt-4o-mini",
        api_key: Optional[str] = None
    ):
        """
        Initialize OpenAI provider

        Args:
            model_name: OpenAI model name (e.g., 'gpt-4o-mini', 'gpt-4o')
            api_key: OpenAI API key (uses OPENAI_API_KEY env var if not provided)
        """
        super().__init__(model_name=model_name)
        self.client = AsyncOpenAI(api_key=api_key)

    async def generate(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None
    ) -> GenerationResponse:
        """
        Generate text using OpenAI

        Args:
            prompt: Input prompt
            config: Generation configuration

        Returns:
            GenerationResponse with generated text
        """
        config = config or GenerationConfig()

        messages = [{"role": "user", "content": prompt}]

        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                top_p=config.top_p,
                stop=config.stop,
                stream=False
            )

            return GenerationResponse(
                content=response.choices[0].message.content or "",
                model=response.model,
                finish_reason=response.choices[0].finish_reason,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                } if response.usage else None
            )
        except Exception as e:
            logger.error(f"Error generating with OpenAI: {e}")
            raise

    async def chat(
        self,
        messages: List[Message],
        config: Optional[GenerationConfig] = None
    ) -> GenerationResponse:
        """
        Generate chat completion using OpenAI

        Args:
            messages: List of chat messages
            config: Generation configuration

        Returns:
            GenerationResponse with assistant message
        """
        config = config or GenerationConfig()

        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=openai_messages,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                top_p=config.top_p,
                stop=config.stop,
                stream=False
            )

            return GenerationResponse(
                content=response.choices[0].message.content or "",
                model=response.model,
                finish_reason=response.choices[0].finish_reason,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                } if response.usage else None
            )
        except Exception as e:
            logger.error(f"Error with OpenAI chat: {e}")
            raise

    async def stream(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None
    ) -> AsyncIterator[str]:
        """
        Stream generated text from OpenAI

        Args:
            prompt: Input prompt
            config: Generation configuration

        Yields:
            Generated text chunks
        """
        config = config or GenerationConfig()

        messages = [{"role": "user", "content": prompt}]

        try:
            stream = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                top_p=config.top_p,
                stop=config.stop,
                stream=True
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"Error streaming from OpenAI: {e}")
            raise

    async def chat_stream(
        self,
        messages: List[Message],
        config: Optional[GenerationConfig] = None
    ) -> AsyncIterator[str]:
        """
        Stream chat completion from OpenAI

        Args:
            messages: List of chat messages
            config: Generation configuration

        Yields:
            Generated text chunks
        """
        config = config or GenerationConfig()

        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        try:
            stream = await self.client.chat.completions.create(
                model=self.model_name,
                messages=openai_messages,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                top_p=config.top_p,
                stop=config.stop,
                stream=True
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"Error streaming chat from OpenAI: {e}")
            raise
