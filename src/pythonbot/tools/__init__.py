from pythonbot.tools.exec_tool import ExecTool
from pythonbot.tools.filesystem import ReadFileTool, WriteFileTool, ListDirectoryTool
from pythonbot.tools.web_search import WebSearchTool
from pythonbot.tools.web_fetch import WebFetchTool
from pythonbot.tools.system_info import SystemInfoTool
from pythonbot.tools.code_exec import CodeExecuteTool
from pythonbot.tools.browser import BrowserScreenshotTool
from pythonbot.tools.patch import ApplyPatchTool
from pythonbot.tools.tts_tool import TTSTool
from pythonbot.tools.stt_tool import STTTool

from pythonbot.tools.registry import tool_registry

# Registra ferramentas iniciais no ambiente
tool_registry.register(ExecTool())
tool_registry.register(ReadFileTool())
tool_registry.register(WriteFileTool())
tool_registry.register(ListDirectoryTool())
tool_registry.register(WebSearchTool())
tool_registry.register(WebFetchTool())
tool_registry.register(SystemInfoTool())
tool_registry.register(CodeExecuteTool())
tool_registry.register(BrowserScreenshotTool())
tool_registry.register(ApplyPatchTool())
tool_registry.register(TTSTool())
tool_registry.register(STTTool())

def init_tools():
    """Initializes built-in tools. Can be called on app startup."""
    pass
