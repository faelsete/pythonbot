import asyncio
from typing import Any
from pythonbot.tools.base import BaseTool

class ExecTool(BaseTool):
    name = "exec"
    description = "Executa um comando no shell do sistema operacional e retorna a saída (stdout/stderr)."
    parameters_schema = {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "O comando a ser executado."
            },
            "background": {
                "type": "boolean",
                "description": "Se verdadeiro, roda o processo em background e apenas retorna o PID."
            }
        },
        "required": ["command"]
    }

    async def execute(self, command: str, background: bool = False) -> Any:
        if background:
            # Roda no background sem esperar
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            return f"Processo iniciado em background com PID {process.pid}"
        else:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            output = ""
            if stdout:
                output += f"STDOUT:\n{stdout.decode('utf-8', errors='replace')}\n"
            if stderr:
                output += f"STDERR:\n{stderr.decode('utf-8', errors='replace')}\n"
                
            return output.strip() or "Comando executado com sucesso (sem saída)."
