"""
Anthropic provider for Claude models
"""
import logging
from typing import List, Optional, AsyncIterator
from anthropic import AsyncAnthropic
from .base import GenerationProvider, GenerationConfig, GenerationResponse, Message

logger = logging.getLogger(__name__)


class AnthropicProvider(GenerationProvider):
    """Anthropic provider for Claude models"""

    def __init__(
        self,
        model_name: str = "claude-3-5-sonnet-20241022",
        api_key: Optional[str] = None
    ):
        """
        Initialize Anthropic provider

        Args:
            model_name: Anthropic model name (e.g., 'claude-3-5-sonnet-20241022', 'claude-3-5-haiku-20241022')
            api_key: Anthropic API key (uses ANTHROPIC_API_KEY env var if not provided)
        """
        super().__init__(model_name=model_name)
        self.client = AsyncAnthropic(api_key=api_key)

    async def generate(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None
    ) -> GenerationResponse:
        """
        Generate text using Anthropic

        Args:
            prompt: Input prompt
            config: Generation configuration

        Returns:
            GenerationResponse with generated text
        """
        config = config or GenerationConfig()

        messages = [{"role": "user", "content": prompt}]

        try:
            response = await self.client.messages.create(
                model=self.model_name,
                messages=messages,
                max_tokens=config.max_tokens or 1024,
                temperature=config.temperature,
                top_p=config.top_p,
                stop_sequences=config.stop
            )

            return GenerationResponse(
                content=response.content[0].text if response.content else "",
                model=response.model,
                finish_reason=response.stop_reason,
                usage={
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens
                } if response.usage else None
            )
        except Exception as e:
            logger.error(f"Error generating with Anthropic: {e}")
            raise

    async def chat(
        self,
        messages: List[Message],
        config: Optional[GenerationConfig] = None
    ) -> GenerationResponse:
        """
        Generate chat completion using Anthropic

        Args:
            messages: List of chat messages
            config: Generation configuration

        Returns:
            GenerationResponse with assistant message
        """
        config = config or GenerationConfig()

        # Separate system message if present
        system_message = None
        anthropic_messages = []

        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                anthropic_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

        try:
            kwargs = {
                "model": self.model_name,
                "messages": anthropic_messages,
                "max_tokens": config.max_tokens or 1024,
                "temperature": config.temperature,
                "top_p": config.top_p,
            }

            if system_message:
                kwargs["system"] = system_message
            if config.stop:
                kwargs["stop_sequences"] = config.stop

            response = await self.client.messages.create(**kwargs)

            return GenerationResponse(
                content=response.content[0].text if response.content else "",
                model=response.model,
                finish_reason=response.stop_reason,
                usage={
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens
                } if response.usage else None
            )
        except Exception as e:
            logger.error(f"Error with Anthropic chat: {e}")
            raise

    async def stream(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None
    ) -> AsyncIterator[str]:
        """
        Stream generated text from Anthropic

        Args:
            prompt: Input prompt
            config: Generation configuration

        Yields:
            Generated text chunks
        """
        config = config or GenerationConfig()

        messages = [{"role": "user", "content": prompt}]

        try:
            async with self.client.messages.stream(
                model=self.model_name,
                messages=messages,
                max_tokens=config.max_tokens or 1024,
                temperature=config.temperature,
                top_p=config.top_p,
                stop_sequences=config.stop
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        except Exception as e:
            logger.error(f"Error streaming from Anthropic: {e}")
            raise

    async def chat_stream(
        self,
        messages: List[Message],
        config: Optional[GenerationConfig] = None
    ) -> AsyncIterator[str]:
        """
        Stream chat completion from Anthropic

        Args:
            messages: List of chat messages
            config: Generation configuration

        Yields:
            Generated text chunks
        """
        config = config or GenerationConfig()

        # Separate system message if present
        system_message = None
        anthropic_messages = []

        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                anthropic_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

        try:
            kwargs = {
                "model": self.model_name,
                "messages": anthropic_messages,
                "max_tokens": config.max_tokens or 1024,
                "temperature": config.temperature,
                "top_p": config.top_p,
            }

            if system_message:
                kwargs["system"] = system_message
            if config.stop:
                kwargs["stop_sequences"] = config.stop

            async with self.client.messages.stream(**kwargs) as stream:
                async for text in stream.text_stream:
                    yield text
        except Exception as e:
            logger.error(f"Error streaming chat from Anthropic: {e}")
            raise
