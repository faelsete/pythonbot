"""Modelos Pydantic compartilhados entre todos os módulos do Pythonbot."""

from typing import Optional
from pydantic import BaseModel


class Message(BaseModel):
    """Representa uma mensagem no histórico de conversa."""
    role: str
    content: str
    name: Optional[str] = None


class ProviderResponse(BaseModel):
    """Resposta padronizada de qualquer provider LLM."""
    content: str
    tokens_used: int = 0
    model: str = ""
    finish_reason: Optional[str] = None
    tool_calls: Optional[list] = None
