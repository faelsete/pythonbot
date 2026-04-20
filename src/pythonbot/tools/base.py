from abc import ABC, abstractmethod
from typing import Dict, Any, Callable

class BaseTool(ABC):
    """
    Abstract base class for all tools.
    """
    name: str = ""
    description: str = ""
    parameters_schema: Dict[str, Any] = {}

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """
        Executa a ferramenta com os argumentos providenciados.
        Retorna o resultado da execução (geralmente uma string ou dict).
        """
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Returns JSON Schema compatible format representing the tool.
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters_schema
            }
        }
