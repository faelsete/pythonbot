import httpx
from typing import Any
from pythonbot.tools.base import BaseTool

class WebSearchTool(BaseTool):
    name = "web_search"
    description = "Pesquisa na web usando DuckDuckGo Lite (gratuito) ou Brave Search caso API esteja configurada."
    parameters_schema = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Termo a ser pesquisado"}
        },
        "required": ["query"]
    }

    async def execute(self, query: str) -> Any:
        # Usando a API não documentada lite do DDG HTML como fallback open source gratuito 
        # (Para uso real e production usaríamos python-duckduckgo-search ou Brave API)
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://html.duckduckgo.com/html/", 
                    params={"q": query},
                    headers={"User-Agent": "Mozilla/5.0"}
                )
                if resp.status_code == 200:
                    # Simplificação para a fase 2 inicial: extração muito crua.
                    # Recomendado importar BeautifulSoup aqui futuramente.
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    results = []
                    for a in soup.find_all('a', class_='result__snippet'):
                        results.append(a.text)
                    if results:
                        return "\n---\n".join(results[:5])
                    return "Nenhum resultado encontrado."
                return f"Erro DuckDuckGo: Status {resp.status_code}"
        except Exception as e:
            return f"Erro na pesquisa web: {str(e)}"
