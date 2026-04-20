import asyncio
import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table

from pythonbot.core.session import session_manager
from pythonbot.core.context import ContextAssembler
from pythonbot.commands.slash import parse_and_route_slash

console = Console()


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """Pythonbot — Agente AI Organismo Vivo."""
    if ctx.invoked_subcommand is None:
        interactive_session()


def interactive_session():
    """Loop interativo principal do CLI."""
    console.print(Panel.fit(
        "[bold blue]Pythonbot[/bold blue] v0.1.0 — Organismo Vivo Iniciado\n"
        "Digite '/help' para comandos ou 'exit' para sair."
    ))

    # Ensure tools are registered
    import pythonbot.tools  # noqa: F401

    while True:
        try:
            active_sid = session_manager.active_session_id
            user_input = Prompt.ask(f"\n[bold green]Sessão {active_sid}[/bold green] You")

            if user_input.strip().lower() in ["exit", "quit"]:
                console.print("[dim]Até logo.[/dim]")
                break

            if user_input.startswith("/"):
                result = parse_and_route_slash(user_input)
                console.print(f"\n{result}")
                continue

            asyncio.run(_process_message(user_input))

        except KeyboardInterrupt:
            console.print("\n[dim]Interrompido.[/dim]")
            break
        except Exception as e:
            console.print(f"[bold red]Erro: {str(e)}[/bold red]")


async def _process_message(msg: str):
    """Stream LLM response in real-time."""
    from pythonbot.core.session import session_manager
    from pythonbot.core.context import ContextAssembler
    from pythonbot.core.models import Message
    from pythonbot.core.config import settings
    from pythonbot.providers.registry import registry
    from pythonbot.tools.registry import tool_registry
    import json
    import sys

    sess = session_manager.get_session(session_manager.active_session_id)
    provider = registry.get_provider(registry.active_provider)

    if not provider:
        console.print("[red]Erro: Nenhum provider LLM configurado.[/red]")
        return

    if not provider.api_key and "localhost" not in provider.base_url:
        console.print("[red]⚠️ API Key não configurada. Use: uv run pythonbot setup[/red]")
        return

    sess.add_message("user", msg)

    ctx = ContextAssembler()
    system_prompt = ctx.assemble(sess.id, sess.tokens_used, sess.created_at)
    context_messages = ctx.compress(sess.messages)
    tools = tool_registry.get_all_schemas()
    current_messages = [Message(role="system", content=system_prompt)] + context_messages

    # Agentic loop
    for loop_idx in range(5):
        try:
            # Try streaming first (text-only, no tools on stream)
            if loop_idx == 0 and not any(kw in msg.lower() for kw in [
                "execute", "rode", "crie", "arquivo", "pesquise", "busque",
                "screenshot", "fale", "ouça", "patch", "lista"
            ]):
                # Simple conversation — stream it
                console.print("\n[bold purple]Pythonbot:[/bold purple]")
                full_response = ""
                async for chunk in provider.chat_stream(
                    messages=current_messages,
                    model=provider.models[0],
                ):
                    sys.stdout.write(chunk)
                    sys.stdout.flush()
                    full_response += chunk
                print()  # newline
                sess.add_message("assistant", full_response or "(Resposta vazia)")
                return

            # Tool-capable path (non-streaming)
            response = await provider.chat(
                messages=current_messages,
                model=provider.models[0],
                tools=tools if tools else None,
            )
            sess.tokens_used += response.tokens_used

            if response.tool_calls:
                console.print(f"\n[dim]🔧 Executando tools...[/dim]")
                current_messages.append(
                    Message(role="assistant", content=response.content or "Executando tools...")
                )
                for call in response.tool_calls:
                    tool_name = call["function"]["name"]
                    try:
                        args = json.loads(call["function"]["arguments"])
                    except (json.JSONDecodeError, TypeError):
                        args = {}
                    try:
                        result = await tool_registry.execute_tool(tool_name, **args)
                        console.print(f"[dim]  ✓ {tool_name}[/dim]")
                        tool_msg = f"[Tool '{tool_name}']:\n{result}"
                    except Exception as e:
                        console.print(f"[dim]  ✗ {tool_name}: {e}[/dim]")
                        tool_msg = f"[Erro Tool '{tool_name}']: {e}"
                    current_messages.append(Message(role="user", content=tool_msg))
                continue

            # Final response
            console.print(f"\n[bold purple]Pythonbot:[/bold purple]\n{response.content}")
            sess.add_message("assistant", response.content or "(Resposta vazia)")
            return

        except Exception as e:
            console.print(f"\n[bold red]Erro: {e}[/bold red]")
            return

    console.print("[yellow]Limite de loops (5) atingido.[/yellow]")


@main.command()
def start():
    """Inicia o daemon FastAPI (Dashboard + API + WebSocket)."""
    import uvicorn
    from pythonbot.core.daemon import app
    from pythonbot.core.config import settings

    console.print(f"[bold]Iniciando daemon em {settings.api_host}:{settings.api_port}...[/bold]")
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)


@main.command()
def setup():
    """Wizard de configuração inicial com menus interativos."""
    from pythonbot.core.config import CONFIG_DIR

    console.print()
    console.print(Panel(
        "[bold cyan]⚡ Pythonbot Setup Wizard[/bold cyan]\n\n"
        "Vamos configurar seu agente AI em 4 passos rápidos.\n"
        "As configurações serão salvas em [dim]~/.pythonbot/config/.env[/dim]",
        border_style="cyan",
    ))

    # ── STEP 1: Provider ────────────────────────────────────
    console.print("\n[bold yellow]PASSO 1/4[/bold yellow] — Provedor LLM\n")

    providers = {
        "1": ("openrouter", "OpenRouter (multi-model, recomendado)", "https://openrouter.ai/api/v1"),
        "2": ("openai", "OpenAI (GPT-4o, GPT-4.1)", "https://api.openai.com/v1"),
        "3": ("anthropic", "Anthropic (Claude Sonnet 4, Haiku)", "https://api.anthropic.com/v1"),
        "4": ("nvidia", "NVIDIA NIM (Llama, Mistral, DeepSeek)", "https://integrate.api.nvidia.com/v1"),
        "5": ("ollama", "Ollama (local, sem API key)", "http://localhost:11434/v1"),
        "6": ("lmstudio", "LM Studio (local, sem API key)", "http://localhost:1234/v1"),
        "7": ("custom", "✏️  Outro / Manual (digitar URL e modelo)", ""),
    }

    table = Table(show_header=True, header_style="bold magenta", box=None, padding=(0, 2))
    table.add_column("#", style="bold cyan", width=3)
    table.add_column("Provider", style="bold white")
    table.add_column("Descrição", style="dim")

    for num, (pid, label, _) in providers.items():
        table.add_row(num, pid if pid != "custom" else "manual", label)

    console.print(table)
    console.print()

    choice = Prompt.ask(
        "Escolha o número do provider",
        choices=["1", "2", "3", "4", "5", "6", "7"],
        default="1"
    )
    provider_id, provider_label, base_url = providers[choice]

    # Manual: user digita tudo
    if provider_id == "custom":
        provider_id = Prompt.ask("  Nome do provider (ex: groq, together, deepinfra)")
        base_url = Prompt.ask("  Base URL da API (ex: https://api.groq.com/openai/v1)")
        provider_label = f"{provider_id} (custom)"

    console.print(f"  ✅ [green]{provider_label}[/green]\n")

    # ── STEP 2: API Key ─────────────────────────────────────
    console.print("[bold yellow]PASSO 2/4[/bold yellow] — API Key\n")

    key_urls = {
        "openrouter": "https://openrouter.ai/keys",
        "openai": "https://platform.openai.com/api-keys",
        "anthropic": "https://console.anthropic.com/settings/keys",
        "nvidia": "https://build.nvidia.com/explore/discover",
    }

    if provider_id in ("ollama", "lmstudio"):
        api_key = "not-needed"
        console.print("  [dim]Provider local — API key não necessária.[/dim]\n")
    else:
        key_url = key_urls.get(provider_id)
        if key_url:
            console.print(f"  Obtenha sua key em: [link]{key_url}[/link]")
        console.print()
        api_key = ""
        while not api_key.strip():
            api_key = Prompt.ask("  Cole sua API Key aqui", password=True)
            if not api_key.strip():
                console.print("  [bold red]❌ API Key é obrigatória para providers cloud. Tente novamente.[/bold red]\n")

    # ── STEP 3: Model ────────────────────────────────────────
    console.print("[bold yellow]PASSO 3/4[/bold yellow] — Modelo Principal\n")

    models_by_provider = {
        "openrouter": {
            "1": ("openai/gpt-4o-mini", "GPT-4o Mini (barato, rápido)"),
            "2": ("openai/gpt-4o", "GPT-4o (poderoso)"),
            "3": ("anthropic/claude-sonnet-4-20250514", "Claude Sonnet 4 (inteligente)"),
            "4": ("google/gemini-2.5-flash-preview", "Gemini 2.5 Flash (rápido)"),
            "5": ("meta-llama/llama-4-maverick", "Llama 4 Maverick (open-source)"),
            "6": ("nvidia/llama-3.3-nemotron-super-49b-v1", "Nemotron Super 49B (NVIDIA)"),
        },
        "openai": {
            "1": ("gpt-4o-mini", "GPT-4o Mini (barato, rápido)"),
            "2": ("gpt-4o", "GPT-4o (poderoso)"),
            "3": ("gpt-4.1-mini", "GPT-4.1 Mini (novo)"),
        },
        "anthropic": {
            "1": ("claude-sonnet-4-20250514", "Claude Sonnet 4"),
            "2": ("claude-3-5-haiku-20241022", "Claude 3.5 Haiku (rápido)"),
        },
        "nvidia": {
            "1": ("meta/llama-3.3-70b-instruct", "Llama 3.3 70B Instruct"),
            "2": ("nvidia/llama-3.3-nemotron-super-49b-v1", "Nemotron Super 49B"),
            "3": ("deepseek-ai/deepseek-r1", "DeepSeek R1"),
            "4": ("mistralai/mistral-large-2-instruct", "Mistral Large 2"),
            "5": ("google/gemma-2-27b-it", "Gemma 2 27B"),
        },
        "ollama": {
            "1": ("llama3.2", "Llama 3.2 (8B)"),
            "2": ("qwen2.5", "Qwen 2.5 (7B)"),
            "3": ("mistral", "Mistral (7B)"),
        },
        "lmstudio": {
            "1": ("local-model", "Modelo carregado no LM Studio"),
        },
    }

    available_models = models_by_provider.get(provider_id, {})

    if available_models:
        # Adiciona opção manual ao final
        next_num = str(len(available_models) + 1)
        available_models[next_num] = ("__manual__", "✏️  Digitar modelo manualmente")

        model_table = Table(show_header=True, header_style="bold magenta", box=None, padding=(0, 2))
        model_table.add_column("#", style="bold cyan", width=3)
        model_table.add_column("Modelo", style="bold white")
        model_table.add_column("Info", style="dim")

        for num, (model_id, desc) in available_models.items():
            display_id = model_id if model_id != "__manual__" else "manual"
            model_table.add_row(num, display_id, desc)

        console.print(model_table)
        console.print()

        model_choices = list(available_models.keys())
        model_choice = Prompt.ask(
            "Escolha o número do modelo",
            choices=model_choices,
            default="1"
        )
        model = available_models[model_choice][0]

        if model == "__manual__":
            model = Prompt.ask("  Digite o nome completo do modelo (ex: meta/llama-3.3-70b-instruct)")
    else:
        # Provider custom/desconhecido — input direto
        model = Prompt.ask("  Digite o nome do modelo")

    console.print(f"  ✅ [green]{model}[/green]\n")

    # ── STEP 4: Telegram ─────────────────────────────────────
    console.print("[bold yellow]PASSO 4/4[/bold yellow] — Telegram Bot (opcional)\n")

    tg_token = ""
    if Confirm.ask("  Deseja configurar um bot Telegram?", default=False):
        console.print("  Crie um bot via [link]https://t.me/BotFather[/link] e copie o token.\n")
        tg_token = Prompt.ask("  Token do bot", password=True)

    # ── SAVE ─────────────────────────────────────────────────
    env_path = CONFIG_DIR / ".env"
    lines = [
        f"LLM_PROVIDER={provider_id}",
        f"LLM_API_KEY={api_key}",
        f"LLM_MODEL={model}",
        f"LLM_BASE_URL={base_url}",
    ]
    if tg_token:
        lines.append(f"TELEGRAM_BOT_TOKEN={tg_token}")

    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # ── SUMMARY ──────────────────────────────────────────────
    console.print()
    summary = Table(title="Configuração Salva", show_header=False, border_style="green", padding=(0, 2))
    summary.add_column("Key", style="bold")
    summary.add_column("Value", style="cyan")
    summary.add_row("Provider", provider_label)
    summary.add_row("Modelo", model)
    summary.add_row("API Key", api_key[:8] + "..." if len(api_key) > 8 else "***")
    summary.add_row("Base URL", base_url)
    summary.add_row("Telegram", "Configurado" if tg_token else "Não configurado")
    summary.add_row("Arquivo", str(env_path))
    console.print(summary)

    console.print(f"\n[bold green]✅ Pronto![/bold green] Execute:")
    console.print(f"  [cyan]uv run pythonbot[/cyan]          — CLI interativo")
    console.print(f"  [cyan]uv run pythonbot start[/cyan]    — Daemon + Dashboard\n")


if __name__ == "__main__":
    main()
