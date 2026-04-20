#!/bin/bash
set -e

echo "======================================"
echo "    Pythonbot - Setup Automático"
echo "======================================"

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_DIR"

# 1. ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "⚙️  Instalando ffmpeg..."
    sudo apt update && sudo apt install -y ffmpeg
fi

# 2. uv
if ! command -v uv &> /dev/null; then
    echo "⚙️  Instalando uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
    if ! grep -q '.local/bin' "$HOME/.bashrc" 2>/dev/null; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
    fi
fi

# 3. Node (para MCPs)
if ! command -v npm &> /dev/null; then
    echo "⚙️  Instalando Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

# 4. Dependências Python
echo "📦 Instalando dependências..."
uv sync

# 5. Playwright (opcional)
echo "🕸️  Instalando Playwright..."
uv run playwright install chromium --with-deps 2>/dev/null || echo "⚠️  Playwright falhou (opcional)"

# 6. Diretórios
mkdir -p "$HOME/.pythonbot/config"
mkdir -p "$HOME/.pythonbot/data/skills"

echo ""
echo "✅ Instalação completa!"
echo ""
echo "Comandos (do diretório raiz do repo):"
echo "  uv run pythonbot setup    # Wizard de configuração"
echo "  uv run pythonbot          # CLI interativo"  
echo "  uv run pythonbot start    # Daemon + Dashboard"
echo ""
echo "Iniciando wizard de configuração..."
echo ""

uv run pythonbot setup
