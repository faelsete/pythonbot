from typing import Any, List, Dict
import os
from pythonbot.tools.base import BaseTool

class ApplyPatchTool(BaseTool):
    name = "apply_patch"
    description = "Aplica patches múltiplos (alterações) em um arquivo."
    parameters_schema = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Arquivo alvo."},
            "chunks": {
                "type": "array",
                "description": "Lista de chunks para substituir",
                "items": {
                    "type": "object",
                    "properties": {
                        "search": {"type": "string", "description": "Texto a ser procurado e substituído"},
                        "replace": {"type": "string", "description": "Texto substituto"}
                    },
                    "required": ["search", "replace"]
                }
            }
        },
        "required": ["path", "chunks"]
    }

    async def execute(self, path: str, chunks: List[Dict[str, str]]) -> Any:
        try:
            if not os.path.exists(path):
                return f"Erro: Arquivo '{path}' não existe."
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for chunk in chunks:
                search = chunk.get("search", "")
                replace = chunk.get("replace", "")
                if search in content:
                    content = content.replace(search, replace)
                else:
                    return f"Erro: Trecho exato '{search}' não encontrado no arquivo."
                    
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            return f"Patch aplicado com sucesso em {path}."
        except Exception as e:
            return f"Erro ao aplicar patch: {str(e)}"
