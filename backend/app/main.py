"""
PSICOAPOIO - Assistente Terapêutico
API Principal com WebSocket
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
from pathlib import Path
from loguru import logger

from config import settings
from services.stt_service import STTService
from services.tts_service import TTSService
from services.llm_service import LLMService
from services.avatar_service import AvatarService
from websocket.voice_handler import VoiceHandler

app = FastAPI(title="PsicoVoz", version="1.0.0")

stt_service = None
tts_service = None
llm_service = None
avatar_service = None

VALID_APPROACHES = [
    "psicanalise", "psicanalise_freud", "psicanalise_lacan", "psicanalise_jung",
    "gestalt", "gestalt_fritz", "gestalt_laura", "gestalt_zinker",
    "tcc", "behaviorismo", "tcc_beck", "tcc_ellis", "tcc_judith",
]

@app.on_event("startup")
async def startup():
    global stt_service, tts_service, llm_service, avatar_service
    logger.info("=" * 50)
    logger.info("🧠 PSICOAPOIO - Iniciando...")
    logger.info("=" * 50)
    stt_service = STTService()
    tts_service = TTSService()
    llm_service = LLMService()
    avatar_service = AvatarService()
    logger.info("✅ Todos os servicos inicializados")

@app.on_event("shutdown")
async def shutdown():
    logger.info("🛑 PsicoVoz encerrado")

@app.get("/")
async def root():
    return {"app": "PsicoVoz", "version": "1.0.0", "status": "online"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/app")
async def serve_app():
    # Caminho correto: /app/frontend/web/index.html (conforme docker-compose volumes)
    frontend_path = Path("/app/frontend/web/index.html")
    
    if frontend_path.exists():
        return FileResponse(frontend_path, media_type="text/html")
    
    return HTMLResponse("<h1>PsicoVoz</h1><p>Frontend não encontrado</p>")

@app.websocket("/ws/voice/{approach}")
async def websocket_voice(websocket: WebSocket, approach: str):
    if approach not in VALID_APPROACHES:
        await websocket.close(code=4000)
        return
    
    await websocket.accept()
    logger.info(f"🔗 WebSocket conectado: {approach}")
    
    try:
        handler = VoiceHandler(
            websocket=websocket,
            approach=approach,
            stt_service=stt_service,
            tts_service=tts_service,
            llm_service=llm_service,
            avatar_service=avatar_service
        )
        await handler.run()
    except WebSocketDisconnect:
        logger.info("🔌 WebSocket desconectado")
    except Exception as e:
        logger.error(f"❌ Erro WebSocket: {e}")
