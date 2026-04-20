"""
Interface Telegram usando aiogram v3 — suporte nativo a grupos, middleware, filtros compostos.
Equivalente Python do grammY (que é exclusivo JS/TS).
"""
import logging
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message as TgMessage
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart

from pythonbot.core.config import settings
from pythonbot.core.session import session_manager
from pythonbot.interfaces.voice import voice_manager

logger = logging.getLogger(__name__)

# Router principal — equivalente ao Composer do grammY
router = Router(name="main")


def _check_auth(user_id: int) -> bool:
    """Verifica se o user_id está autorizado (vazio = sem restrição)."""
    if settings.telegram_allowed_users and user_id not in settings.telegram_allowed_users:
        logger.warning(f"Usuário não autorizado: {user_id}")
        return False
    return True


# ── Commands ────────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: TgMessage):
    """Handler para /start — funciona em privado e em grupos."""
    await message.answer(
        "🤖 *Pythonbot* — Organismo Vivo\\.\n"
        "Use /help para ver comandos disponíveis\\.",
        parse_mode=ParseMode.MARKDOWN_V2,
    )


@router.message(Command("help"))
async def cmd_help(message: TgMessage):
    await message.answer(
        "Comandos:\n"
        "/status — Status do sistema\n"
        "/voice — Ativa/desativa respostas em áudio\n"
        "/listen — Ativa/desativa STT (Whisper)\n"
        "/session — Gerencia sessões (new/list/kill)"
    )


@router.message(Command("status"))
async def cmd_status(message: TgMessage):
    from pythonbot.commands.slash import parse_and_route_slash
    result = parse_and_route_slash("/status")
    await message.answer(result)


@router.message(Command("voice"))
async def cmd_voice(message: TgMessage):
    from pythonbot.commands.slash import parse_and_route_slash
    args = message.text.split()[1:] if message.text else []
    cmd = "/voice " + " ".join(args) if args else "/voice"
    result = parse_and_route_slash(cmd)
    await message.answer(result)


@router.message(Command("listen"))
async def cmd_listen(message: TgMessage):
    from pythonbot.commands.slash import parse_and_route_slash
    args = message.text.split()[1:] if message.text else []
    cmd = "/listen " + " ".join(args) if args else "/listen"
    result = parse_and_route_slash(cmd)
    await message.answer(result)


@router.message(Command("session"))
async def cmd_session(message: TgMessage):
    from pythonbot.commands.slash import parse_and_route_slash
    args = message.text.split()[1:] if message.text else []
    cmd = "/session " + " ".join(args) if args else "/session"
    result = parse_and_route_slash(cmd)
    await message.answer(result)


@router.message(Command("doctor"))
async def cmd_doctor(message: TgMessage):
    from pythonbot.commands.slash import parse_and_route_slash
    args = message.text.split()[1:] if message.text else []
    cmd = "/doctor " + " ".join(args) if args else "/doctor"
    result = parse_and_route_slash(cmd)
    await message.answer(result)


# ── Text Messages (private + groups) ───────────────────────

@router.message(F.text & ~F.text.startswith("/"))
async def handle_text(message: TgMessage):
    """Processa mensagens de texto (funciona em chats privados e grupos)."""
    if not _check_auth(message.from_user.id):
        return

    text = message.text
    if not text:
        return

    await _route_and_reply(message, text)


# ── Voice Messages ──────────────────────────────────────────

@router.message(F.voice)
async def handle_voice(message: TgMessage):
    """Processa mensagens de voz via Whisper STT."""
    if not _check_auth(message.from_user.id):
        return

    if not voice_manager.listen_mode_enabled:
        await message.answer("Modo STT desativado. Use /listen para habilitar.")
        return

    import tempfile
    import os

    # Download do áudio
    bot = message.bot
    file = await bot.get_file(message.voice.file_id)
    tmp_path = os.path.join(tempfile.gettempdir(), f"tg_audio_{message.message_id}.ogg")
    await bot.download_file(file.file_path, tmp_path)

    # Transcrever
    from pythonbot.tools.stt_tool import STTTool
    stt = STTTool()
    transcribed = await stt.execute(tmp_path)

    if "Erro" in transcribed:
        await message.answer(transcribed)
        return

    await message.answer(f"🎤 Transcrição: {transcribed}")
    await _route_and_reply(message, transcribed)


# ── Core Pipeline ───────────────────────────────────────────

async def _route_and_reply(message: TgMessage, text: str):
    """Rota texto pelo LLM pipeline e responde."""
    from pythonbot.core.router import router_engine

    sess = session_manager.get_session(session_manager.active_session_id)
    if not sess:
        await message.answer("Erro: Nenhuma sessão ativa.")
        return

    # Indicador de "digitando" — UX melhor em grupos
    await message.bot.send_chat_action(message.chat.id, "typing")

    response_text = await router_engine.process_user_input(sess.id, text)

    # Modo voz: responde com áudio
    if voice_manager.voice_mode_enabled:
        try:
            from pythonbot.tools.tts_tool import TTSTool
            tts = TTSTool()
            filepath_msg = await tts.execute(response_text, voice_manager.current_voice)

            if filepath_msg and "Erro" not in filepath_msg:
                from aiogram.types import FSInputFile
                audio_path = filepath_msg.split(": ", 1)[-1].strip()
                voice_file = FSInputFile(audio_path)
                await message.answer_voice(voice=voice_file)
                return
        except Exception as e:
            logger.error(f"Falha TTS: {e}")

    # Resposta em texto (trunca se exceder limite do Telegram)
    max_len = 4096
    if len(response_text) > max_len:
        for i in range(0, len(response_text), max_len):
            await message.answer(response_text[i:i + max_len])
    else:
        await message.answer(response_text)


# ── Inicialização ──────────────────────────────────────────

def create_telegram_bot() -> tuple[Bot, Dispatcher] | None:
    """Cria e configura o bot Telegram com aiogram."""
    if not settings.telegram_bot_token:
        logger.warning("Telegram Bot Token ausente. Bot desativado.")
        return None

    bot = Bot(token=settings.telegram_bot_token)
    dp = Dispatcher()
    dp.include_router(router)

    logger.info("Telegram bot (aiogram) configurado e pronto.")
    return bot, dp


async def start_telegram_polling():
    """Inicia o bot em modo long polling (para desenvolvimento)."""
    result = create_telegram_bot()
    if not result:
        return

    bot, dp = result
    logger.info("Iniciando Telegram polling...")
    await dp.start_polling(bot)
