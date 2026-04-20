from typing import Any
from pythonbot.tools.base import BaseTool


class STTTool(BaseTool):
    name = "stt_transcribe"
    description = "Transcreve arquivo de áudio para texto usando Whisper (tiny)."
    parameters_schema = {
        "type": "object",
        "properties": {
            "audio_path": {"type": "string", "description": "Caminho absoluto do arquivo de áudio"}
        },
        "required": ["audio_path"]
    }

    _model = None  # Class-level lazy-loaded model

    async def execute(self, audio_path: str) -> Any:
        try:
            import whisper
            import os

            if not os.path.exists(audio_path):
                return f"Erro: Arquivo '{audio_path}' não encontrado."

            if STTTool._model is None:
                STTTool._model = whisper.load_model("tiny")

            result = STTTool._model.transcribe(audio_path)
            return result.get("text", "")

        except ImportError:
            return "Erro: Biblioteca 'openai-whisper' não encontrada. Execute: uv add openai-whisper"
        except Exception as e:
            return f"Erro na transcrição STT: {str(e)}"
