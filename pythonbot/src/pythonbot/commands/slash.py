from pythonbot.core.session import session_manager
from pythonbot.interfaces.voice import voice_manager
from pythonbot.skills.manager import skill_manager


def parse_and_route_slash(command_str: str) -> str:
    """Roteador universal de comandos de barra para CLI e Telegram."""
    parts = command_str.strip().split()
    if not parts:
        return "Comando vazio."

    cmd = parts[0].lower()
    args = parts[1:]

    if cmd == "/help":
        return (
            "Comandos Globais:\n"
            "  /status          — Status do sistema (CPU, RAM, sessão)\n"
            "  /session [sub]   — new | list | kill <id> | switch <id>\n"
            "  /provider <nome> — Troca provedor ativo\n"
            "  /model <nome>    — Troca modelo ativo\n"
            "  /config          — Mostra configuração atual\n"
            "  /config set K V  — Altera configuração\n"
            "  /skills          — Lista skills\n"
            "  /voice [on/off]  — Áudio nas respostas\n"
            "  /listen [on/off] — Habilita STT (Whisper)\n"
            "  /doctor          — Diagnóstico completo\n"
            "  /doctor fix      — Diagnóstico + sugestões de reparo\n"
            "  /clear           — Limpa tela\n"
            "  /tokens          — Consumo de tokens da sessão"
        )

    elif cmd == "/status":
        sid = session_manager.active_session_id
        sess = session_manager.get_session(sid)
        tokens = sess.tokens_used if sess else 0
        n_sessions = len(session_manager.list_sessions())
        return f"Sistema Online | Sessão Ativa: {sid} | Tokens: {tokens} | Sessões: {n_sessions}/3"

    elif cmd == "/session":
        if not args:
            return "Uso: /session [new|list|kill <id>|switch <id>]"
        act = args[0]
        if act == "new":
            try:
                s = session_manager.create_session()
                session_manager.active_session_id = s.id
                return f"Sessão nova aberta: {s.id}"
            except ValueError as e:
                return str(e)
        elif act == "list":
            lines = []
            for s in session_manager.list_sessions():
                marker = " ← ativa" if s.id == session_manager.active_session_id else ""
                lines.append(f"  ID: {s.id} | Main: {s.is_main} | Tokens: {s.tokens_used}{marker}")
            return "Sessões:\n" + "\n".join(lines)
        elif act in ["switch", "kill"] and len(args) > 1:
            sid = args[1]
            if act == "switch":
                if session_manager.get_session(sid):
                    session_manager.active_session_id = sid
                    return f"Trocado para sessão {sid}"
                return "Sessão não existe."
            elif act == "kill":
                if session_manager.kill_session(sid):
                    return f"Sessão {sid} encerrada."
                return "Sessão inválida ou é a sessão principal."
        return "Uso: /session [new|list|kill <id>|switch <id>]"

    elif cmd == "/provider":
        if not args:
            from pythonbot.providers.registry import registry
            return f"Provider ativo: {registry.active_provider}\nDisponíveis: {', '.join(registry.list_providers())}"
        from pythonbot.providers.registry import registry
        name = args[0]
        if registry.set_active(name):
            return f"Provider trocado para: {name}"
        return f"Provider '{name}' não registrado."

    elif cmd == "/model":
        if not args:
            from pythonbot.core.config import settings
            return f"Modelo ativo: {settings.llm_model}"
        from pythonbot.providers.registry import registry
        provider = registry.get_provider(registry.active_provider)
        if provider:
            provider.models[0] = args[0]
            return f"Modelo trocado para: {args[0]}"
        return "Nenhum provider ativo."

    elif cmd == "/config":
        if not args:
            from pythonbot.core.config import settings
            return (
                f"Provider: {settings.llm_provider}\n"
                f"Modelo: {settings.llm_model}\n"
                f"Base URL: {settings.llm_base_url}\n"
                f"API Port: {settings.api_port}\n"
                f"Voice: {settings.enable_voice}\n"
                f"STT: {settings.enable_stt}"
            )
        if args[0] == "set" and len(args) >= 3:
            key, value = args[1], " ".join(args[2:])
            return f"⚠️ Para alterar '{key}', edite ~/.pythonbot/config/.env e reinicie."
        return "Uso: /config ou /config set <chave> <valor>"

    elif cmd == "/voice":
        if not args:
            state = voice_manager.toggle_voice_mode()
        else:
            state = voice_manager.toggle_voice_mode(args[0].lower() == "on")
        return f"Voice Mode: {'✅ Ativado' if state else '❌ Desativado'}"

    elif cmd == "/listen":
        if not args:
            state = voice_manager.toggle_listen_mode()
        else:
            state = voice_manager.toggle_listen_mode(args[0].lower() == "on")
        return f"Listen Mode (STT): {'✅ Ativado' if state else '❌ Desativado'}"

    elif cmd == "/skills":
        sks = skill_manager.list_skills()
        if not sks:
            return "Nenhuma skill encontrada."
        lines = [f"  • {s['name']}: {s.get('description', 'Sem descrição')}" for s in sks]
        return "Skills:\n" + "\n".join(lines)

    elif cmd == "/doctor":
        from pythonbot.doctor.reporter import doctor_reporter
        report = doctor_reporter.generate_report()
        if args and args[0] == "fix":
            from pythonbot.doctor.repair import doctor_repair
            fixes = doctor_repair.auto_repair()
            if fixes:
                report += "\n\nSugestões de reparo:\n" + "\n".join(f"  → {f}" for f in fixes)
            else:
                report += "\n\n✅ Nenhum reparo necessário."
        return report

    elif cmd == "/tokens":
        sid = session_manager.active_session_id
        sess = session_manager.get_session(sid)
        return f"Sessão {sid}: {sess.tokens_used if sess else 0} tokens consumidos"

    elif cmd == "/clear":
        return "\033[2J\033[H"  # ANSI clear screen

    elif cmd == "/reset":
        sid = session_manager.active_session_id
        sess = session_manager.get_session(sid)
        if sess:
            sess.messages.clear()
            sess.tokens_used = 0
            return f"Sessão {sid} resetada (memória preservada)."
        return "Nenhuma sessão ativa."

    return f"Comando não reconhecido: {cmd}. Use /help para ver comandos."
