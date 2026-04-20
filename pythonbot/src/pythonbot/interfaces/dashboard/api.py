from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from pythonbot.core.session import session_manager
from pythonbot.skills.manager import skill_manager
from pythonbot.doctor.diagnostics import doctor_diagnostics

api_router = APIRouter()


class MessagePayload(BaseModel):
    message: str
    session_id: Optional[str] = None


@api_router.get("/status")
async def get_status():
    return {
        "status": "online",
        "doctor": doctor_diagnostics.check_all()
    }


@api_router.get("/sessions")
async def get_sessions():
    sessions = session_manager.list_sessions()
    return [{"id": s.id, "tokens": s.tokens_used, "is_main": s.is_main} for s in sessions]


@api_router.get("/skills")
async def get_skills():
    return skill_manager.list_skills()


@api_router.post("/message")
async def post_message(payload: MessagePayload):
    """Process a message through the LLM pipeline via REST API."""
    from pythonbot.core.router import router_engine

    sess_id = payload.session_id or session_manager.active_session_id
    sess = session_manager.get_session(sess_id)
    if not sess:
        return {"error": "Sessão inválida", "session": sess_id}

    response = await router_engine.process_user_input(sess.id, payload.message)
    return {"response": response, "session": sess_id}
