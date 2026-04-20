from typing import Any
import asyncio
from pythonbot.tools.base import BaseTool

class TTSTool(BaseTool):
    name = "tts_speak"
    description = "Converte texto em áudio usando Edge TTS e retorna o caminho do arquivo gerado."
    parameters_schema = {
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "Texto a ser convertido para áudio"},
            "voice": {"type": "string", "description": "Opções: pt-BR-FranciscaNeural, pt-BR-AntonioNeural, etc. Default: pt-BR-FranciscaNeural"}
        },
        "required": ["text"]
    }

    async def execute(self, text: str, voice: str = "pt-BR-FranciscaNeural") -> Any:
        try:
            import edge_tts
            import tempfile
            from pathlib import Path
            
            output_file = Path(tempfile.gettempdir()) / f"tts_output_{asyncio.get_running_loop().time()}.mp3"
            
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(str(output_file))
            
            return f"Áudio gerado com sucesso em: {output_file}"
        except ImportError:
            return "Erro: Biblioteca 'edge-tts' não encontrada. Execute: uv add edge-tts"
        except Exception as e:
            return f"Erro ao gerar áudio TTS: {str(e)}"
