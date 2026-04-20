#!/bin/bash
set -e

echo "======================================"
echo "    Pythonbot - Setup Inicial Linux"
echo "======================================"

# Verifica dependencias de sistema (Ubuntu/Debian)
if ! command -v ffmpeg &> /dev/null; then
    echo "⚙️  Instalando ffmpeg..."
    sudo apt update && sudo apt install -y ffmpeg
fi

if ! command -v uv &> /dev/null; then
    echo "⚙️  Instalando uv (Fast Python Package Installer)..."
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # uv instala em ~/.local/bin — precisa estar no PATH
    export PATH="$HOME/.local/bin:$PATH"

    # Persiste no bashrc se ainda não estiver
    if ! grep -q '.local/bin' "$HOME/.bashrc" 2>/dev/null; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
    fi
fi

if ! command -v npm &> /dev/null; then
    echo "⚙️  Instalando Node.js (necessário para MCPs)..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

echo "📦 Instalando dependências do Pythonbot..."
cd pythonbot
uv sync

echo "🕸️ Instalando Playwright Chromium..."
uv run playwright install chromium --with-deps 2>/dev/null || echo "⚠️  Playwright falhou (opcional, browser_screenshot não funcionará)"

# Cria wrapper para rodar de qualquer lugar
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
cat > "$REPO_DIR/run.sh" << 'RUNEOF'
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR/pythonbot" && uv run pythonbot "$@"
RUNEOF
chmod +x "$REPO_DIR/run.sh"

echo ""
echo "✅ Setup Finalizado!"
echo ""
echo "Comandos (de qualquer lugar dentro do repo):"
echo "  ./run.sh setup    # Wizard de configuração"
echo "  ./run.sh          # CLI interativo"
echo "  ./run.sh start    # Daemon + Dashboard (porta 8420)"
echo ""
echo "Iniciando wizard de configuração..."
echo ""

# Auto-lança o wizard
cd "$REPO_DIR/pythonbot" && uv run pythonbot setup
