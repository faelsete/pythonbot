import httpx
from typing import List, Dict, Optional, AsyncGenerator
import json

from pythonbot.providers.base import BaseProvider
from pythonbot.core.models import Message, ProviderResponse


class OpenAICompatibleProvider(BaseProvider):
    """
    Provider OpenAI-compatible: OpenRouter, OpenAI, Anthropic, NVIDIA NIM,
    Ollama, LM Studio, Groq, Together, etc.
    """

    def __init__(self, name: str, models: List[str], base_url: str = "https://api.openai.com/v1", api_key: str = ""):
        super().__init__(name, models, base_url, api_key)

    def _headers(self) -> Dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        if "openrouter.ai" in self.base_url:
            headers["HTTP-Referer"] = "https://github.com/faelsete/pythonbot"
            headers["X-Title"] = "Pythonbot"
        return headers

    def _build_payload(self, messages: List[Message], model: str,
                       tools: Optional[List[Dict]] = None, stream: bool = False) -> Dict:
        formatted = [{"role": m.role, "content": m.content} for m in messages]
        payload: Dict = {"model": model, "messages": formatted, "stream": stream}
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        return payload

    async def chat(self, messages: List[Message], model: str,
                   tools: Optional[List[Dict]] = None) -> ProviderResponse:
        """Non-streaming chat completion."""
        payload = self._build_payload(messages, model, tools)

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers(),
                json=payload
            )

            if resp.status_code != 200:
                try:
                    err_msg = resp.json().get("error", {}).get("message", resp.text[:300])
                except Exception:
                    err_msg = resp.text[:300]
                raise RuntimeError(f"LLM API erro {resp.status_code}: {err_msg}")

            data = resp.json()
            choice = data["choices"][0]
            msg = choice["message"]
            usage = data.get("usage", {})

            raw_tool_calls = msg.get("tool_calls")
            return ProviderResponse(
                content=msg.get("content", ""),
                tokens_used=usage.get("total_tokens", 0),
                model=model,
                finish_reason="tool_calls" if raw_tool_calls else choice.get("finish_reason"),
                tool_calls=raw_tool_calls or [],
            )

    async def chat_stream(self, messages: List[Message], model: str,
                          tools: Optional[List[Dict]] = None) -> AsyncGenerator[str, None]:
        """Streaming chat — yields text chunks as they arrive."""
        payload = self._build_payload(messages, model, tools, stream=True)

        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers=self._headers(),
                json=payload
            ) as resp:
                if resp.status_code != 200:
                    body = await resp.aread()
                    raise RuntimeError(f"LLM API erro {resp.status_code}: {body.decode()[:300]}")

                async for line in resp.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data_str = line[6:]
                    if data_str.strip() == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data_str)
                        delta = chunk["choices"][0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
                    except (json.JSONDecodeError, KeyError, IndexError):
                        continue
