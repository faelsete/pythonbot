import httpx
from typing import Any
from pythonbot.tools.base import BaseTool

class WebFetchTool(BaseTool):
    name = "web_fetch"
    description = "Baixa o conteúdo em texto limpo (Markdown) de uma URL."
    parameters_schema = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "URL para capturar o conteúdo"}
        },
        "required": ["url"]
    }

    async def execute(self, url: str) -> Any:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(url, headers={"User-Agent": "Pythonbot/0.1.0"})
                res.raise_for_status()
                
                content_type = res.headers.get("Content-Type", "")
                if "text/html" in content_type:
                    try:
                        import markdownify
                        # Converte HTML limpo pra markdown
                        md_text = markdownify.markdownify(res.text, heading_style="ATX")
                        return md_text
                    except ImportError:
                        return "Biblioteca 'markdownify' não instalada. HTML cru (cortado): \n" + res.text[:2000]
                else:
                    # JSON, Texto plano
                    return res.text[:5000] # truncate
                    
        except Exception as e:
            return f"Falha ao buscar URL: {str(e)}"
