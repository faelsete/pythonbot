from typing import Any
import asyncio
from pythonbot.tools.base import BaseTool

class CodeExecuteTool(BaseTool):
    name = "code_execute"
    description = "Executa código Python num ambiente sandbox (processo filho isolado) e retorna a saída."
    parameters_schema = {
        "type": "object",
        "properties": {
            "code": {
                "type": "string", 
                "description": "Código Python puro para executar. Pode usar `print()` para retornar valores."
            }
        },
        "required": ["code"]
    }

    async def execute(self, code: str) -> Any:
        # Grava código em arquivo temp
        import tempfile
        import os
        
        try:
            fd, path = tempfile.mkstemp(suffix=".py")
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # Execute timeout 10 seconds
            process = await asyncio.create_subprocess_exec(
                "python", path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30.0)
            except asyncio.TimeoutError:
                process.kill()
                return "Erro: O script Python demorou muito (>30s) e foi morto."
            finally:
                os.unlink(path) # Limpeza
                
            out_str = stdout.decode('utf-8', errors='replace').strip()
            err_str = stderr.decode('utf-8', errors='replace').strip()
            
            res = ""
            if out_str:
                res += f"Saída (STDOUT):\n{out_str}\n"
            if err_str:
                res += f"Erros (STDERR):\n{err_str}"
            
            return res if res else "(Nenhuma saída retornada. Use print() para ver algo.)"
            
        except Exception as e:
            return f"Erro no sandbox Python: {str(e)}"
