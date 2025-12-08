# ============================================================================
# ClimAPI - Túnel Pinggy.io Runner
# ============================================================================
# Script simple para iniciar el túnel Pinggy desde PowerShell
# Uso: .\run-tunnel.ps1
#
# Nota: Este script es lo más simple posible. Solo ejecuta pinggy.exe
# ============================================================================

# Configuración
$TUNNEL_CMD = "pinggy.exe"
$PORT = "443"
$LOCAL_IP = "127.0.0.1"
$LOCAL_PORT = "8501"
$TOKEN = "Fm4hH7kZ8sz+force"
$HOST = "free.pinggy.io"
$SSH_OPTIONS = "-o StrictHostKeyChecking=no -o ServerAliveInterval=30"

# Comando completo
$CMD = "$TUNNEL_CMD -p $PORT -R0:${LOCAL_IP}:${LOCAL_PORT} $SSH_OPTIONS ${TOKEN}@${HOST}"

# Banner
Clear-Host
Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║              🌐 CLIMAPI DASHBOARD - PINGGY.IO TUNNEL                      ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "⏳ Iniciando túnel..." -ForegroundColor Yellow
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

# Ejecutar el comando
try {
    # Intentar con pinggy.exe
    & $TUNNEL_CMD -p $PORT -R0:${LOCAL_IP}:${LOCAL_PORT} $SSH_OPTIONS ${TOKEN}@${HOST}
}
catch {
    Write-Host "❌ Error: pinggy.exe no encontrado" -ForegroundColor Red
    Write-Host ""
    Write-Host "Opciones:" -ForegroundColor Yellow
    Write-Host "  1. Descarga pinggy.exe desde https://pinggy.io/" -ForegroundColor Cyan
    Write-Host "  2. Colócalo en este directorio" -ForegroundColor Cyan
    Write-Host "  3. O agrega pinggy.exe a tu PATH" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Alternativa: Usa el script Python" -ForegroundColor Green
    Write-Host "  python pinggy_direct.py" -ForegroundColor Cyan
    Write-Host ""
}
