import asyncio
from typing import Any

async def run_mcp_server():
    """Inicia o Pythonbot como um servidor MCP via stdio."""
    try:
        from mcp.server import Server
        from mcp.server.stdio import stdio_server
        from pythonbot.tools.registry import tool_registry
        
        # Cria servidor MCP nomeado
        app = Server("pythonbot-mcp")
        
        # Injeta automaticamente todas ferramentas built-in do pythonbot para o mundo externo
        @app.list_tools()
        async def list_tools() -> list:
            import mcp.types as types
            tools = []
            for schema in tool_registry.get_all_schemas():
                func = schema["function"]
                tools.append(types.Tool(
                    name=func["name"],
                    description=func["description"],
                    inputSchema=func["parameters"]
                ))
            return tools

        @app.call_tool()
        async def call_tool(name: str, arguments: dict) -> list:
            import mcp.types as types
            try:
                res = await tool_registry.execute_tool(name, **arguments)
                return [types.TextContent(type="text", text=str(res))]
            except Exception as e:
                return [types.TextContent(type="text", text=f"Erro MCP Server: {e}")]
                
        async with stdio_server() as (read_stream, write_stream):
            await app.run(read_stream, write_stream, app.create_initialization_options())
            
    except ImportError:
        print("Módulo mcp ausente.")
