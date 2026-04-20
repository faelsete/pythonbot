import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pythonbot.tools.system_info import SystemInfoTool
from pythonbot.core.session import session_manager

ws_router = APIRouter()
sys_info = SystemInfoTool()

@ws_router.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Mandar info de sistema pra real-time plot
            import psutil
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            
            # Mandar o contador de tokens da sessao ativa
            sid = session_manager.active_session_id
            sess = session_manager.get_session(sid)
            tokens = sess.tokens_used if sess else 0
            
            payload = {
                "type": "heartbeat",
                "cpu": cpu,
                "ram": ram,
                "active_session": sid,
                "tokens": tokens
            }
            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(2) # 2 segundos de interval pra não ser agressivo demais
    except WebSocketDisconnect:
        pass
