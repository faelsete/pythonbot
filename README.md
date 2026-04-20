# 🤖 Pythonbot
**Um agente AI local-first que funciona como organismo vivo no sistema operacional.**

## 🌟 O que é?
Diferente de modelos genéricos ou instâncias temporárias, o **Pythonbot** é um Daemon desenhado para viver na sua máquina. Ele sabe quem você é, possui memória relacional semântica (MemPalace) persistente e age não apenas como assistente de chat, mas como um **operador de SO** dotado de Voice, Web-Scraping, Executáveis de Terminal e integrações profundas usando o Model Context Protocol (MCP).

## ✨ Principais Funcionalidades
- **Organismo Vivo:** Roda em background na sua máquina e pode ser acessado de qualquer lugar via Telegram Bot, Terminal Interativo ou Dashboard Web.
- **Multimodal (Voz e Audíção):** Intercepte mensagens de áudio do Telegram e transforme-as em texto magicamente usando Whisper (tiny). Responde em MP3 fluentes usando a biblioteca Microsoft Edge TTS neural.
- **Memória de Elefante (MemPalace):** Seu contexto nunca se apaga ao fechar o terminal. Grava pedaços úteis em banco vetorial/JSON local para resgate rápido.
- **Ecossistema MCP:** Converse diretamente com seu Banco de Dados, Notion, Web Browser ou Sistema de Arquivos acoplando subservidores MCP locais sem escrever sequer uma linha de códio para a API deles.
- **Skills Crontabs:** Defina blocos lógicos `.yaml` de tarefas (como "Olhar os logs, limpar o lixo do tmp, mandar email") que o agente constrói pra você.

---

## 🛠 Como Instalar

> **Pré-requisitos**:
> - Python 3.11+
> - Node/NPM (Obrigatório se for usar integrações MCP)

### 👉 Passo 1: Clone 
\`\`\`bash
git clone https://github.com/SeuUsuario/pythonbot.git
cd pythonbot
\`\`\`

### 👉 Passo 2: Rode o setup
- Usando **Linux / WSL / MacOS**:
  \`\`\`bash
  bash setup.sh
  \`\`\`

- Usando **Windows PowerShell**:
  \`\`\`powershell
  .\setup.ps1
  \`\`\`

*(Ele instalará o `uv` e todas as dependências isoladamente e super rápido).*

### 👉 Passo 3: Inicie

Terminal Rápido Neural:
\`\`\`bash
cd pythonbot && uv run pythonbot
\`\`\`

Iniciar Daemon/Dashboard:
\`\`\`bash
cd pythonbot && uv run pythonbot start
\`\`\`
*(Acesse http://localhost:8420 para a visão 3D/SPA Web)*.

---

## 👨‍💻 Feito com Filosofia "Karpathy's LLM Config"
- **Simplicidade:** Código imperativo e legível. Configs por Pydantic Settings. Nada abstraído que não pudesse ser quebrado em 2 min.
- **Goals Driven:** Orientação cirúrgica.

## 🤝 Contribuições & Licença
Licença MIT. Fique a vontade para dar forks!
