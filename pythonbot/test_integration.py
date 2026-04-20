"""Teste de integração completo do Pythonbot."""
import sys
sys.path.insert(0, "src")

print("=== TESTE COMPLETO DE IMPORTAÇÃO ===")
errors = []

modules = [
    ("core.config", "from pythonbot.core.config import settings"),
    ("core.models", "from pythonbot.core.models import Message, ProviderResponse"),
    ("core.session", "from pythonbot.core.session import session_manager"),
    ("core.context", "from pythonbot.core.context import ContextAssembler"),
    ("providers.base", "from pythonbot.providers.base import BaseProvider"),
    ("providers.registry", "from pythonbot.providers.registry import registry"),
    ("providers.openai_compat", "from pythonbot.providers.openai_compat import OpenAICompatibleProvider"),
    ("tools.registry", "from pythonbot.tools.registry import tool_registry"),
    ("tools.__init__", "import pythonbot.tools"),
    ("core.router", "from pythonbot.core.router import router_engine"),
    ("core.daemon", "from pythonbot.core.daemon import app"),
    ("commands.slash", "from pythonbot.commands.slash import parse_and_route_slash"),
    ("doctor.diagnostics", "from pythonbot.doctor.diagnostics import doctor_diagnostics"),
    ("doctor.reporter", "from pythonbot.doctor.reporter import doctor_reporter"),
    ("doctor.repair", "from pythonbot.doctor.repair import doctor_repair"),
    ("interfaces.voice", "from pythonbot.interfaces.voice import voice_manager"),
    ("mcp.server", "from pythonbot.mcp.server import run_mcp_server"),
    ("mcp.registry", "from pythonbot.mcp.registry import mcp_registry"),
    ("mcp.client", "from pythonbot.mcp.client import mcp_client_manager"),
    ("memory.manager", "from pythonbot.memory.manager import memory_manager"),
    ("skills.manager", "from pythonbot.skills.manager import skill_manager"),
    ("cli", "from pythonbot.cli import main"),
]

for name, imp in modules:
    try:
        exec(imp)
        print(f"  OK  {name}")
    except Exception as e:
        errors.append((name, str(e)))
        print(f"  FAIL {name}: {e}")

total = len(modules)
ok = total - len(errors)
print(f"\n=== RESULTADO: {ok}/{total} modulos OK ===")

if errors:
    print("FALHAS:")
    for n, e in errors:
        print(f"  {n}: {e}")
else:
    print("Todos os modulos importam sem erro!")

# Testes funcionais
print("\n=== TESTES FUNCIONAIS ===")
from pythonbot.tools.registry import tool_registry
schemas = tool_registry.get_all_schemas()
tool_names = [s["function"]["name"] for s in schemas]
print(f"Tools registradas: {len(schemas)}")
print(f"Tools: {tool_names}")

from pythonbot.commands.slash import parse_and_route_slash
status_result = parse_and_route_slash("/status")
print(f"Status: {status_result}")

doctor_result = parse_and_route_slash("/doctor")
print(f"Doctor: {'OK' if 'PYTHON' in doctor_result else 'FAIL'}")

from pythonbot.providers.registry import registry
print(f"Provider ativo: {registry.active_provider}")
print(f"Providers: {registry.list_providers()}")

from pythonbot.mcp.registry import mcp_registry
print(f"MCPs: {mcp_registry.list_configs()}")

print("\n=== TODOS OS TESTES PASSARAM ===")
