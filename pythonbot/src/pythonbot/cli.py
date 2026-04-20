import asyncio
import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

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
    """Process a user message through the LLM pipeline."""
    from pythonbot.core.router import router_engine

    with console.status("[bold cyan]Pythonbot está pensando...[/bold cyan]", spinner="bouncingBar"):
        response = await router_engine.process_user_input(
            session_manager.active_session_id, msg
        )

    console.print(f"\n[bold purple]Pythonbot:[/bold purple]\n{response}")


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
    """Wizard de configuração inicial."""
    console.print(Panel("[bold]Setup Wizard[/bold] — Configuração do Pythonbot"))

    from pythonbot.core.config import CONFIG_DIR

    # Provider
    provider = Prompt.ask("Provedor LLM", default="openrouter",
                          choices=["openrouter", "openai", "anthropic", "ollama", "lmstudio"])
    api_key = Prompt.ask("API Key (será salva em ~/.pythonbot/config/.env)", password=True)
    model = Prompt.ask("Modelo principal", default="openai/gpt-4o-mini")

    # Telegram
    tg_token = Prompt.ask("Token do Bot Telegram (vazio para pular)", default="")

    # Save to .env
    env_path = CONFIG_DIR / ".env"
    lines = [
        f"LLM_PROVIDER={provider}",
        f"LLM_API_KEY={api_key}",
        f"LLM_MODEL={model}",
    ]
    if tg_token:
        lines.append(f"TELEGRAM_BOT_TOKEN={tg_token}")

    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    console.print(f"\n[green]✅ Configuração salva em {env_path}[/green]")
    console.print("Execute [bold]pythonbot[/bold] para iniciar ou [bold]pythonbot start[/bold] para o daemon.")


if __name__ == "__main__":
    main()
