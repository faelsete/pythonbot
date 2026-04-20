from typing import Optional
from pythonbot.core.config import settings

class VoiceManager:
    """Gerencia configurações de voz da sessão atual/ambiente."""
    
    def __init__(self):
        self.voice_mode_enabled = settings.enable_voice
        self.listen_mode_enabled = settings.enable_stt
        self.current_voice = "pt-BR-FranciscaNeural"

    def toggle_voice_mode(self, state: Optional[bool] = None) -> bool:
        if state is not None:
            self.voice_mode_enabled = state
        else:
            self.voice_mode_enabled = not self.voice_mode_enabled
        return self.voice_mode_enabled

    def toggle_listen_mode(self, state: Optional[bool] = None) -> bool:
        if state is not None:
            self.listen_mode_enabled = state
        else:
            self.listen_mode_enabled = not self.listen_mode_enabled
        return self.listen_mode_enabled
        
    def set_voice(self, voice_name: str):
        self.current_voice = voice_name
        return self.current_voice

voice_manager = VoiceManager()
