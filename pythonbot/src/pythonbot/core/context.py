from pathlib import Path
from datetime import datetime
from pythonbot.core.config import CONFIG_DIR
from pythonbot.core.models import Message

USER_MD_PATH = CONFIG_DIR / "user.md"
RULES_MD_PATH = CONFIG_DIR / "rules.md"
CONTEXT_MD_PATH = CONFIG_DIR / "context.md"


def _ensure_files_exist():
    """Create default config files if they don't exist."""
    if not USER_MD_PATH.exists():
        USER_MD_PATH.write_text(
            "# Perfil do Usuário\n\n**Nome:** [Não configurado]\n**Idioma preferido:** pt-BR\n",
            encoding="utf-8"
        )
    if not RULES_MD_PATH.exists():
        RULES_MD_PATH.write_text(
            "# Regras Globais Obrigatórias\n\n"
            "1. **Think Before Coding**: Não assuma. Não esconda confusão.\n"
            "2. **Simplicity First**: Código mínimo que resolve o problema.\n"
            "3. **Surgical Changes**: Toque apenas no necessário.\n"
            "4. **Goal-Driven Execution**: Defina critérios de sucesso.\n",
            encoding="utf-8"
        )
    if not CONTEXT_MD_PATH.exists():
        CONTEXT_MD_PATH.write_text(
            "# Contexto da Sessão\n\n"
            "**Sessão ID:** {session_id}\n"
            "**Iniciada:** {started_at}\n"
            "**Tokens usados:** {tokens_used}\n",
            encoding="utf-8"
        )


class ContextAssembler:
    def __init__(self):
        _ensure_files_exist()

    def assemble(self, session_id: str, tokens_used: int, started_at: datetime) -> str:
        """
        Assembles the system prompt combining rules, user profile, and session context.
        """
        user_content = USER_MD_PATH.read_text(encoding="utf-8")
        rules_content = RULES_MD_PATH.read_text(encoding="utf-8")
        context_template = CONTEXT_MD_PATH.read_text(encoding="utf-8")

        session_context = context_template.format(
            session_id=session_id,
            started_at=started_at.strftime("%Y-%m-%d %H:%M:%S"),
            tokens_used=tokens_used
        )

        return f"{rules_content}\n\n{user_content}\n\n{session_context}"

    def compress(self, session_messages: list[Message]) -> list[Message]:
        """
        Compressão inteligente de contexto.
        Mantém o system prompt, a primeira e as últimas mensagens intactas.
        """
        if len(session_messages) < 10:
            return list(session_messages)

        system_msgs = [m for m in session_messages if m.role == "system"]
        first_system = system_msgs[0] if system_msgs else session_messages[0]
        recent = session_messages[-5:]

        middle = Message(
            role="system",
            content=f"[... Contexto comprimido. {len(session_messages) - 6} mensagens anteriores omitidas para preservação de janela ...]"
        )

        return [first_system, middle] + recent
