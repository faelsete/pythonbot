import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from pythonbot.core.config import settings
from pythonbot.core.session import session_manager
from pythonbot.interfaces.voice import voice_manager

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def _check_auth(user_id: int) -> bool:
    """Verifica se o user_id está autorizado."""
    if settings.telegram_allowed_users and user_id not in settings.telegram_allowed_users:
        logger.warning(f"Usuário não autorizado: {user_id}")
        return False
    return True


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Pythonbot — Organismo Vivo. Autenticado.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Comandos:\n"
        "/status - Status do bot\n"
        "/voice [on/off] - Alterna respostas em áudio\n"
        "/listen [on/off] - Ativa STT (Whisper)\n"
        "/session [new/list] - Gerencia sessões"
    )


async def _route_and_reply(update: Update, text: str):
    """Rota texto pelo LLM e responde ao usuário."""
    from pythonbot.core.router import router_engine

    sess = session_manager.get_session(session_manager.active_session_id)
    if not sess:
        await update.message.reply_text("Erro: Nenhuma sessão ativa.")
        return

    response_text = await router_engine.process_user_input(sess.id, text)

    if voice_manager.voice_mode_enabled:
        try:
            from pythonbot.tools.tts_tool import TTSTool
            tts = TTSTool()
            filepath_msg = await tts.execute(response_text, voice_manager.current_voice)

            if filepath_msg and "Erro" not in filepath_msg:
                audio_path = filepath_msg.split(": ", 1)[-1].strip()
                with open(audio_path, "rb") as audio_file:
                    await update.message.reply_voice(voice=audio_file)
                return
        except Exception as e:
            logger.error(f"Falha TTS: {e}")

    await update.message.reply_text(response_text)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _check_auth(update.effective_user.id):
        return

    text = update.message.text
    if not text:
        return

    await _route_and_reply(update, text)


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _check_auth(update.effective_user.id):
        return

    if not voice_manager.listen_mode_enabled:
        await update.message.reply_text("Modo STT desativado. Use /listen on para habilitar.")
        return

    new_file = await update.message.voice.get_file()
    import tempfile
    import os
    tmp_path = os.path.join(tempfile.gettempdir(), f"telegram_audio_{update.update_id}.ogg")
    await new_file.download_to_drive(tmp_path)

    from pythonbot.tools.stt_tool import STTTool
    stt = STTTool()
    transcribed = await stt.execute(tmp_path)

    if "Erro" in transcribed:
        await update.message.reply_text(transcribed)
        return

    await update.message.reply_text(f"🎤 Transcrição: {transcribed}")

    # Processa o texto transcrito pelo pipeline normal
    await _route_and_reply(update, transcribed)


def init_telegram_bot() -> Application | None:
    if not settings.telegram_bot_token:
        logger.warning("Telegram Bot Token ausente. Bot desativado.")
        return None

    app = Application.builder().token(settings.telegram_bot_token).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    logger.info("Telegram bot registrado.")
    return app
