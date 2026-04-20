import httpx
from typing import List, Dict, Optional
import json

from pythonbot.providers.base import BaseProvider
from pythonbot.core.models import Message, ProviderResponse


class OpenAICompatibleProvider(BaseProvider):
    """
    Provedor flexível que cobre OpenAI, OpenRouter, LM Studio e outras APIs 100% compatíveis.
    """

    def __init__(self, name: str, models: List[str], base_url: str = "https://api.openai.com/v1", api_key: str = ""):
        super().__init__(name, models, base_url, api_key)

    async def chat(self, messages: List[Message], model: str, tools: Optional[List[Dict]] = None) -> ProviderResponse:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # OpenRouter specific headers
        if "openrouter.ai" in self.base_url:
            headers["HTTP-Referer"] = "https://github.com/pythonbot/pythonbot"
            headers["X-Title"] = "Pythonbot"

        formatted_messages = []
        for m in messages:
            msg: Dict = {"role": m.role, "content": m.content}
            if m.name:
                msg["name"] = m.name
            formatted_messages.append(msg)

        payload: Dict = {
            "model": model,
            "messages": formatted_messages,
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )

            if resp.status_code != 200:
                try:
                    err = resp.json()
                    err_msg = err.get("error", {}).get("message", resp.text[:300])
                except Exception:
                    err_msg = resp.text[:300]
                raise RuntimeError(
                    f"LLM API erro {resp.status_code}: {err_msg}"
                )

            data = resp.json()

            choice = data["choices"][0]
            message_info = choice["message"]
            finish_reason = choice.get("finish_reason")
            usage = data.get("usage", {})
            tokens_used = usage.get("total_tokens", 0)

            # Checa se o modelo chamou ferramentas
            raw_tool_calls = message_info.get("tool_calls")
            if raw_tool_calls:
                return ProviderResponse(
                    content=message_info.get("content", ""),
                    tokens_used=tokens_used,
                    model=model,
                    finish_reason="tool_calls",
                    tool_calls=raw_tool_calls,
                )

            # Resposta padrão de texto
            return ProviderResponse(
                content=message_info.get("content", ""),
                tokens_used=tokens_used,
                model=model,
                finish_reason=finish_reason,
            )
