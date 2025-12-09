#!/usr/bin/env powershell
# ============================================================================
# ClimAPI - SSH Tunnel (Alternativa a Pinggy.exe)
# ============================================================================
# Inicia un túnel SSH a Pinggy.io sin necesidad de pinggy.exe
# Uso: .\run-tunnel-ssh.ps1
# ============================================================================

# Configuración
$TOKEN = "Fm4hH7kZ8sz+force"
$HOST = "free.pinggy.io"
$LOCAL_PORT = "8501"
$SSH_OPTIONS = "-o StrictHostKeyChecking=no -o ServerAliveInterval=30"

# Comando SSH
$CMD = "ssh -R 0:localhost:$LOCAL_PORT $SSH_OPTIONS ${TOKEN}@${HOST}"

# Banner
Clear-Host
Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║            🌐 CLIMAPI DASHBOARD - SSH TUNNEL (PINGGY.IO)                  ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "⏳ Iniciando túnel SSH..." -ForegroundColor Yellow
Write-Host ""
Write-Host "📊 Dashboard Local:" -ForegroundColor Green
Write-Host "   🔗 http://localhost:8501" -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 Dashboard Remoto (HTTPS):" -ForegroundColor Green
Write-Host "   🔗 https://Fm4hH7kZ8sz.free.pinggy.io" -ForegroundColor Cyan
Write-Host ""
Write-Host "─────────────────────────────────────────────────────────────────────────────" -ForegroundColor DarkGray
Write-Host ""

# Mostrar el comando
Write-Host "📋 Comando ejecutado:" -ForegroundColor Yellow
Write-Host "$CMD" -ForegroundColor DarkGray
Write-Host ""
Write-Host "Presiona Ctrl+C para detener el túnel" -ForegroundColor Magenta
Write-Host ""
Write-Host "─────────────────────────────────────────────────────────────────────────────" -ForegroundColor DarkGray
Write-Host ""

# Ejecutar el comando SSH
try {
    # Ejecutar SSH directamente
    & ssh -R 0:localhost:$LOCAL_PORT $SSH_OPTIONS ${TOKEN}@${HOST}
}
catch {
    Write-Host "❌ Error ejecutando SSH" -ForegroundColor Red
    Write-Host ""
    Write-Host "Posibles soluciones:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Verifica que tengas SSH instalado:" -ForegroundColor Cyan
    Write-Host "   ssh -V" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Si no tienes SSH, instala una de estas opciones:" -ForegroundColor Cyan
    Write-Host "   • Git Bash (https://git-scm.com/)" -ForegroundColor Gray
    Write-Host "   • Windows 10+ ya tiene OpenSSH integrado" -ForegroundColor Gray
    Write-Host "   • OpenSSH para Windows (https://github.com/PowerShell/Win32-OpenSSH)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Alternativa: Usa ngrok" -ForegroundColor Cyan
    Write-Host "   ngrok http 8501" -ForegroundColor Gray
    Write-Host ""
    Write-Host "4. Consulta PINGGY_ALTERNATIVES.md para más opciones" -ForegroundColor Cyan
    Write-Host ""
}
