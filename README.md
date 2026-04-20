# 🤖 Pythonbot

**Um agente AI local-first que funciona como organismo vivo no sistema operacional.**

## 🌟 O que é?

Diferente de modelos genéricos ou instâncias temporárias, o **Pythonbot** é um Daemon desenhado para viver na sua máquina. Ele sabe quem você é, possui memória relacional semântica ([MemPalace](https://github.com/MemPalace/mempalace)) persistente e age não apenas como assistente de chat, mas como um **operador de SO** dotado de Voice, Web-Scraping, Executáveis de Terminal e integrações profundas usando o [Model Context Protocol (MCP)](https://modelcontextprotocol.io/).

## ✨ Funcionalidades

| Feature | Descrição |
|---------|-----------|
| 🧠 **Organismo Vivo** | Daemon em background — acessível via Terminal, Telegram ou Dashboard Web |
| 🔧 **12 Tools Built-in** | exec, filesystem, web_search, web_fetch, browser, code_exec, system_info, tts, stt, patch |
| 🔌 **MCP Nativo** | 6 servidores pré-configurados (Brave Search, Filesystem, GitHub, Playwright, Postgres, Sequential Thinking) |
| 🤖 **Telegram (aiogram v3)** | Suporte a grupos, voz bidirecional, slash commands, indicador de "digitando" |
| 🎤 **Multimodal** | STT (Whisper) + TTS (Microsoft Edge Neural) |
| 🏥 **Doctor & Auto-Repair** | Diagnóstico completo do sistema com sugestões de reparo |
| 📋 **Skills YAML** | Blocos lógicos de tarefas executáveis pelo agente |
| 🌐 **Dashboard Glassmorphism** | Métricas real-time via WebSocket (CPU, RAM, tokens) + Neural Chat |
| 🔓 **Multi-Provider** | OpenRouter, OpenAI, Anthropic, Ollama, LM Studio — qualquer API OpenAI-compatible |

## 📦 Arquitetura

```
src/pythonbot/
├── core/          # Daemon, Router, Session, Context, Config
├── providers/     # LLM providers (OpenAI-compatible)
├── tools/         # 12 ferramentas built-in
├── interfaces/    # Telegram (aiogram), Dashboard (FastAPI+WS)
├── mcp/           # MCP Server + Client + Registry
├── doctor/        # Diagnóstico e auto-reparo
├── skills/        # Skills YAML manager
├── memory/        # MemPalace integration
└── commands/      # Slash commands unificados
```

## 🛠 Instalação

> **Pré-requisitos**: Python 3.11+ | Node/NPM (para MCPs)

### 1. Clone

```bash
git clone https://github.com/faelsete/pythonbot.git
cd pythonbot
```

### 2. Setup automático

**Linux / WSL / macOS:**
```bash
bash setup.sh
```

**Windows PowerShell:**
```powershell
.\setup.ps1
```

### 3. Configure e use

O `setup.sh` já lança o wizard automaticamente. Depois:

```bash
uv run pythonbot          # CLI interativo
uv run pythonbot start    # Daemon + Dashboard (http://IP:8420)
```

### 5. Docker (opcional)

```bash
cp .env.example .env  # edite com suas keys
docker compose up -d
```

## ⌨️ Comandos

| Comando | Descrição |
|---------|-----------|
| `/help` | Lista todos os comandos |
| `/status` | Status do sistema (sessão, tokens) |
| `/session new\|list\|kill\|switch` | Gerenciamento de sessões (max 3) |
| `/provider <nome>` | Troca provedor LLM ativo |
| `/model <nome>` | Troca modelo ativo |
| `/config` | Mostra configuração atual |
| `/voice [on/off]` | Ativa/desativa respostas em áudio |
| `/listen [on/off]` | Ativa/desativa STT (Whisper) |
| `/doctor` | Diagnóstico completo do sistema |
| `/doctor fix` | Diagnóstico + sugestões de reparo |
| `/tokens` | Consumo de tokens da sessão |
| `/skills` | Lista skills disponíveis |
| `/reset` | Limpa memória da sessão ativa |

## 🔌 Dependências Opcionais

```bash
# Telegram bot
uv add aiogram

# MCP integration
uv add "mcp[cli]"

# Voice (TTS)
uv add edge-tts

# Speech-to-Text
uv add openai-whisper

# Browser screenshots
uv add playwright && playwright install chromium

# Persistent memory
uv add mempalace
```

Ou tudo de uma vez:
```bash
uv add "pythonbot[all]"
```

## 🏥 Doctor

O sistema de diagnóstico verifica automaticamente:
- ✅ Versão do Python
- ✅ ffmpeg (para TTS/STT)
- ✅ Node.js/npx (para MCPs)
- ✅ Bibliotecas críticas (mcp, fastapi)
- ✅ Espaço em disco
- ✅ Configuração do LLM provider

```bash
cd pythonbot && uv run pythonbot
# Dentro do CLI:
/doctor
/doctor fix
```

## 👨‍💻 Filosofia

Construído seguindo os princípios "Karpathy's LLM Config":
- **Simplicidade:** Código imperativo e legível. Nada abstraído desnecessariamente.
- **Goal-Driven:** Orientação cirúrgica — cada módulo faz uma coisa bem.
- **Local-First:** Seus dados ficam na sua máquina. Zero cloud obrigatório.

## 📄 Licença

MIT — veja [LICENSE](LICENSE).

## 🤝 Contribuições

PRs são bem-vindos! Abra uma issue antes para discutir mudanças significativas.
