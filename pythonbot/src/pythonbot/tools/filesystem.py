from typing import Any, List, Optional
from pathlib import Path
from pythonbot.tools.base import BaseTool

class ReadFileTool(BaseTool):
    name = "read_file"
    description = "Read the contents of a file."
    parameters_schema = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Caminho do arquivo"}
        },
        "required": ["path"]
    }

    async def execute(self, path: str) -> Any:
        try:
            return Path(path).read_text(encoding="utf-8")
        except Exception as e:
            return f"Erro ao ler arquivo: {str(e)}"

class WriteFileTool(BaseTool):
    name = "write_file"
    description = "Write or overwrite a file with content."
    parameters_schema = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Caminho do arquivo"},
            "content": {"type": "string", "description": "Conteúdo para escrever"}
        },
        "required": ["path", "content"]
    }

    async def execute(self, path: str, content: str) -> Any:
        try:
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
            return f"Arquivo '{path}' escrito com sucesso."
        except Exception as e:
            return f"Erro ao escrever arquivo: {str(e)}"

class ListDirectoryTool(BaseTool):
    name = "list_directory"
    description = "List files and directories within a given path."
    parameters_schema = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Caminho do diretório"}
        },
        "required": ["path"]
    }

    async def execute(self, path: str) -> Any:
        try:
            p = Path(path)
            if not p.is_dir():
                return f"Erro: '{path}' não é um diretório"
                
            items = []
            for item in p.iterdir():
                tipo = "DIR" if item.is_dir() else "FILE"
                items.append(f"[{tipo}] {item.name}")
            return "\n".join(items) if items else "Diretório vazio."
        except Exception as e:
            return f"Erro ao listar diretório: {str(e)}"
