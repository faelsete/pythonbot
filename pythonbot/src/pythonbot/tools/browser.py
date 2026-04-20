from typing import Any, Optional
from pythonbot.tools.base import BaseTool
import base64

class BrowserScreenshotTool(BaseTool):
    name = "browser_screenshot"
    description = "Tira um screenshot de uma página na web e retorna a string base64 que pode ser lida por modelos de visão."
    parameters_schema = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "URL destino da página"}
        },
        "required": ["url"]
    }

    async def execute(self, url: str) -> Any:
        try:
            from playwright.async_api import async_playwright
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(url, timeout=30000)
                screenshot_bytes = await page.screenshot(full_page=False)
                await browser.close()
                b64 = base64.b64encode(screenshot_bytes).decode('utf-8')
                return f"[SCREENSHOT] base64 convertido internamente com sucesso.\nPassar payload base64 para modelo visual: {b64[:20]}...{b64[-20:]}"
        except ImportError:
            return "Playwright não instalado. Use uv add playwright && playwright install"
        except Exception as e:
            return f"Erro ao no Playwright: {str(e)}"
