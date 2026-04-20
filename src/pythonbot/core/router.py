import json
import logging
from pythonbot.core.session import session_manager
from pythonbot.core.context import ContextAssembler
from pythonbot.core.models import Message
from pythonbot.core.config import settings
from pythonbot.providers.registry import registry
from pythonbot.providers.openai_compat import OpenAICompatibleProvider
from pythonbot.tools.registry import tool_registry

logger = logging.getLogger(__name__)


def _init_default_provider():
    """Initialize the default provider from settings."""
    provider = OpenAICompatibleProvider(
        name=settings.llm_provider,
        models=[settings.llm_model],
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
    )
    registry.register_instance(settings.llm_provider, provider)
    registry.set_active(settings.llm_provider)


_init_default_provider()


class MessageRouter:
    """Coração do Pythonbot — roteia mensagens pelo LLM e resolve tool calls."""

    def __init__(self):
        self.context_assembler = ContextAssembler()

    async def process_user_input(self, session_id: str, text: str) -> str:
        sess = session_manager.get_session(session_id)
        if not sess:
            return "Erro: Sessão inexistente."

        provider = registry.get_provider(registry.active_provider)
        if not provider:
            return "Erro: Nenhum provedor LLM configurado."

        if not provider.api_key and "localhost" not in provider.base_url:
            return (
                "⚠️ API Key não configurada. "
                "Use: uv run pythonbot setup"
            )

        sess.add_message("user", text)

        system_prompt = self.context_assembler.assemble(
            sess.id, sess.tokens_used, sess.created_at
        )

        context_messages = self.context_assembler.compress(sess.messages)
        tools = tool_registry.get_all_schemas()

        # Agentic loop (max 5 tool rounds)
        current_messages = [Message(role="system", content=system_prompt)] + context_messages

        for loop_idx in range(5):
            try:
                logger.info(f"LLM call #{loop_idx}")
                response = await provider.chat(
                    messages=current_messages,
                    model=provider.models[0],
                    tools=tools if tools else None,
                )
                sess.tokens_used += response.tokens_used

                if response.tool_calls:
                    # Tool execution round
                    assistant_content = response.content or ""
                    current_messages.append(
                        Message(role="assistant", content=assistant_content or "Executando tools...")
                    )

                    for call in response.tool_calls:
                        tool_name = call["function"]["name"]
                        try:
                            args = json.loads(call["function"]["arguments"])
                        except (json.JSONDecodeError, TypeError):
                            args = {}

                        try:
                            tool_result = await tool_registry.execute_tool(tool_name, **args)
                            tool_msg = f"[Tool '{tool_name}']:\n{tool_result}"
                        except Exception as e:
                            tool_msg = f"[Erro Tool '{tool_name}']: {e}"

                        current_messages.append(Message(role="user", content=tool_msg))

                    continue

                # Final text response
                final_text = response.content or "(Resposta vazia)"
                sess.add_message("assistant", final_text)
                return final_text

            except Exception as e:
                error_str = f"Erro LLM: {e}"
                logger.error(error_str, exc_info=True)
                sess.add_message("assistant", error_str)
                return error_str

        return "Limite de loops (5) atingido."


router_engine = MessageRouter()
