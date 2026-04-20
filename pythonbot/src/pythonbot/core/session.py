import uuid
from typing import Dict, List, Optional
from datetime import datetime
from pythonbot.core.models import Message


class Session:
    def __init__(self, session_id: str, is_main: bool = False):
        self.id = session_id
        self.is_main = is_main
        self.created_at = datetime.now()
        self.messages: List[Message] = []
        self.tokens_used: int = 0
        self.last_accessed = self.created_at

    def add_message(self, role: str, content: str) -> None:
        self.messages.append(Message(role=role, content=content))
        self.last_accessed = datetime.now()


class SessionManager:
    MAX_SESSIONS = 3

    def __init__(self):
        self._sessions: Dict[str, Session] = {}
        self.active_session_id: Optional[str] = None
        # Create session 0 (main session)
        self.create_session("0", is_main=True)
        self.active_session_id = "0"

    def create_session(self, session_id: Optional[str] = None, is_main: bool = False) -> Session:
        if len(self._sessions) >= self.MAX_SESSIONS and not is_main:
            raise ValueError(f"Máximo de {self.MAX_SESSIONS} sessões atingido. Use /session kill <id> para liberar.")

        sid = session_id or str(uuid.uuid4())[:8]
        new_session = Session(sid, is_main)
        self._sessions[sid] = new_session
        return new_session

    def get_session(self, session_id: str) -> Optional[Session]:
        session = self._sessions.get(session_id)
        if session:
            session.last_accessed = datetime.now()
        return session

    def list_sessions(self) -> List[Session]:
        return list(self._sessions.values())

    def kill_session(self, session_id: str) -> bool:
        session = self._sessions.get(session_id)
        if session and not session.is_main:
            del self._sessions[session_id]
            if self.active_session_id == session_id:
                self.active_session_id = "0"
            return True
        return False


# Global session manager instance
session_manager = SessionManager()
