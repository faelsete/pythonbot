<#
.SYNOPSIS
Instala dependências do Pythonbot em ambientes Windows.
#>

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "    Pythonbot - Setup Inicial Windows" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# Verifica se uv está instalado
if (-not (Get-Command "uv" -ErrorAction SilentlyContinue)) {
    Write-Host "[*] Instalando gerenciador pacote UV..." -ForegroundColor Yellow
    irm https://astral.sh/uv/install.ps1 | iex
    $env:Path += ";$HOME\.cargo\bin"
}

# Informa sobre o ffmpeg
if (-not (Get-Command "ffmpeg" -ErrorAction SilentlyContinue)) {
    Write-Host "[!] AVISO: FFMPEG não foi encontrado. O recurso de Voz/STT precisará do ffmpeg no PATH." -ForegroundColor Red
    Write-Host "Recomendamos: choco install ffmpeg" -ForegroundColor DarkGray
}

Write-Host "[*] Instalando dependências do projeto..." -ForegroundColor Yellow
Set-Location "pythonbot"
uv sync

Write-Host "[*] Instalando drivers do Playwright..." -ForegroundColor Yellow
uv run playwright install chromium

Write-Host ""
Write-Host "✅ Setup Concluído!" -ForegroundColor Green
Write-Host "Para rodar o terminal interativo: cd pythonbot ; uv run pythonbot"
Write-Host "Para rodar o Daemon Web (Dashboard): cd pythonbot ; uv run pythonbot start"
