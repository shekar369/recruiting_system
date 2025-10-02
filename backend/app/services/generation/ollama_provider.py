"""
Ollama provider for local LLM inference
"""
import logging
import aiohttp
from typing import List, Optional, AsyncIterator
from .base import GenerationProvider, GenerationConfig, GenerationResponse, Message

logger = logging.getLogger(__name__)


class OllamaProvider(GenerationProvider):
    """Ollama provider for local LLM inference"""

    def __init__(
        self,
        model_name: str = "llama3.2",
        base_url: str = "http://localhost:11434"
    ):
        """
        Initialize Ollama provider

        Args:
            model_name: Ollama model name (e.g., 'llama3.2', 'mistral')
            base_url: Ollama API base URL
        """
        super().__init__(model_name=model_name, base_url=base_url)
        self.base_url = base_url

    async def generate(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None
    ) -> GenerationResponse:
        """
        Generate text using Ollama

        Args:
            prompt: Input prompt
            config: Generation configuration

        Returns:
            GenerationResponse with generated text
        """
        config = config or GenerationConfig()

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": config.temperature,
                "top_p": config.top_p,
            }
        }

        if config.max_tokens:
            payload["options"]["num_predict"] = config.max_tokens
        if config.stop:
            payload["options"]["stop"] = config.stop

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                ) as response:
                    response.raise_for_status()
                    data = await response.json()

                    return GenerationResponse(
                        content=data.get("response", ""),
                        model=self.model_name,
                        finish_reason=data.get("done_reason"),
                        usage={
                            "prompt_tokens": data.get("prompt_eval_count", 0),
                            "completion_tokens": data.get("eval_count", 0),
                            "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
                        }
                    )
        except Exception as e:
            logger.error(f"Error generating with Ollama: {e}")
            raise

    async def chat(
        self,
        messages: List[Message],
        config: Optional[GenerationConfig] = None
    ) -> GenerationResponse:
        """
        Generate chat completion using Ollama

        Args:
            messages: List of chat messages
            config: Generation configuration

        Returns:
            GenerationResponse with assistant message
        """
        config = config or GenerationConfig()

        payload = {
            "model": self.model_name,
            "messages": [{"role": msg.role, "content": msg.content} for msg in messages],
            "stream": False,
            "options": {
                "temperature": config.temperature,
                "top_p": config.top_p,
            }
        }

        if config.max_tokens:
            payload["options"]["num_predict"] = config.max_tokens
        if config.stop:
            payload["options"]["stop"] = config.stop

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/chat",
                    json=payload
                ) as response:
                    response.raise_for_status()
                    data = await response.json()

                    return GenerationResponse(
                        content=data.get("message", {}).get("content", ""),
                        model=self.model_name,
                        finish_reason=data.get("done_reason"),
                        usage={
                            "prompt_tokens": data.get("prompt_eval_count", 0),
                            "completion_tokens": data.get("eval_count", 0),
                            "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
                        }
                    )
        except Exception as e:
            logger.error(f"Error with Ollama chat: {e}")
            raise

    async def stream(
        self,
        prompt: str,
        config: Optional[GenerationConfig] = None
    ) -> AsyncIterator[str]:
        """
        Stream generated text from Ollama

        Args:
            prompt: Input prompt
            config: Generation configuration

        Yields:
            Generated text chunks
        """
        config = config or GenerationConfig()

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": config.temperature,
                "top_p": config.top_p,
            }
        }

        if config.max_tokens:
            payload["options"]["num_predict"] = config.max_tokens

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                ) as response:
                    response.raise_for_status()

                    async for line in response.content:
                        if line:
                            import json
                            try:
                                data = json.loads(line)
                                if "response" in data:
                                    yield data["response"]
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            logger.error(f"Error streaming from Ollama: {e}")
            raise

    async def chat_stream(
        self,
        messages: List[Message],
        config: Optional[GenerationConfig] = None
    ) -> AsyncIterator[str]:
        """
        Stream chat completion from Ollama

        Args:
            messages: List of chat messages
            config: Generation configuration

        Yields:
            Generated text chunks
        """
        config = config or GenerationConfig()

        payload = {
            "model": self.model_name,
            "messages": [{"role": msg.role, "content": msg.content} for msg in messages],
            "stream": True,
            "options": {
                "temperature": config.temperature,
                "top_p": config.top_p,
            }
        }

        if config.max_tokens:
            payload["options"]["num_predict"] = config.max_tokens

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/chat",
                    json=payload
                ) as response:
                    response.raise_for_status()

                    async for line in response.content:
                        if line:
                            import json
                            try:
                                data = json.loads(line)
                                if "message" in data and "content" in data["message"]:
                                    yield data["message"]["content"]
                            except json.JSONDecodeError:
                                continue
        except Exception as e:
            logger.error(f"Error streaming chat from Ollama: {e}")
            raise
