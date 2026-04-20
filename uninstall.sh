#!/bin/bash
echo "🗑️  Removendo Pythonbot completamente..."

# Remove repo
rm -rf ~/pythonbot

# Remove config e dados
rm -rf ~/.pythonbot

# Remove cache do uv para este projeto
rm -rf ~/.cache/uv 2>/dev/null

echo "✅ Pythonbot removido. Tchau."
