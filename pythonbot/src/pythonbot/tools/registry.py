from typing import Dict, List, Type, Any
from pythonbot.tools.base import BaseTool

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> BaseTool:
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' not found in registry.")
        return self._tools[name]

    def get_all_schemas(self) -> List[Dict[str, Any]]:
        return [tool.get_schema() for tool in self._tools.values()]

    async def execute_tool(self, name: str, **kwargs) -> Any:
        tool = self.get_tool(name)
        return await tool.execute(**kwargs)

# Global tool registry
tool_registry = ToolRegistry()
