from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pythonbot.core.models import Message, ProviderResponse


class BaseProvider(ABC):
    """
    Abstract base class for all LLM providers (OpenAI, Anthropic, Gemini, Ollama, etc.)
    """
    def __init__(self, name: str, models: List[str], base_url: Optional[str] = None, api_key: Optional[str] = None):
        self.name = name
        self.models = models
        self.base_url = base_url or ""
        self.api_key = api_key or ""

    def set_api_key(self, api_key: str) -> None:
        self.api_key = api_key

    @abstractmethod
    async def chat(self, messages: List[Message], model: str, tools: Optional[List[Dict]] = None) -> ProviderResponse:
        """
        Sends messages to the LLM and returns the response.
        """
        pass
