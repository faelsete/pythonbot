import platform
from typing import Any
from pythonbot.tools.base import BaseTool


class SystemInfoTool(BaseTool):
    name = "system_status"
    description = "Obtém informações do sistema (CPU, RAM, disco, rede)."
    parameters_schema = {
        "type": "object",
        "properties": {},
        "required": []
    }

    async def execute(self) -> Any:
        try:
            import psutil

            cpu_pct = psutil.cpu_percent(interval=0.5)
            ram = psutil.virtual_memory()

            # Cross-platform disk check
            disk_path = "C:\\" if platform.system() == "Windows" else "/"
            disk = psutil.disk_usage(disk_path)

            info = [
                f"CPU: {cpu_pct}%",
                f"RAM: {ram.percent}% ({ram.used // (1024**3)}GB / {ram.total // (1024**3)}GB)",
                f"Disco: {disk.percent}% usado ({disk.free // (1024**3)}GB livres de {disk.total // (1024**3)}GB)"
            ]
            return "\n".join(info)
        except ImportError:
            return "Biblioteca 'psutil' não está instalada. Execute: uv add psutil"
        except Exception as e:
            return f"Erro ao ler informações do sistema: {str(e)}"
