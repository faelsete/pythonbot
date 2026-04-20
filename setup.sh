#!/bin/bash
set -e

echo "======================================"
echo "    Pythonbot - Setup Inicial Linux"
echo "======================================"

# Verifica dependencias de sistema (Ubuntu-like simplificado)
if ! command -v ffmpeg &> /dev/null; then
    echo "⚙️  Instalando ffmpeg..."
    sudo apt update && sudo apt install -y ffmpeg
fi

if ! command -v uv &> /dev/null; then
    echo "⚙️  Instalando uv (Fast Python Package Installer)..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

if ! command -v npm &> /dev/null; then
    echo "⚠️  Node/npm ausente. Necessário para instalar MCPs via npx."
    echo "Rode: curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - && sudo apt-get install -y nodejs"
fi

echo "📦 Instalando dependências e bibliotecas do bot..."
cd pythonbot
uv sync

echo "🕸️ Instalando drivers de Browser (Playwright)..."
uv run playwright install chromium

echo ""
echo "✅ Setup Finalizado!"
echo "Para iniciar o Assistente no terminal, rode:"
echo "cd pythonbot && uv run pythonbot"
echo "Para iniciar o Daemon Core e Web Dashboard, rode:"
echo "cd pythonbot && uv run pythonbot start"
