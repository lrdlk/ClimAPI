#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Gestor de Pinggy.io para ClimAPI - Script PowerShell
.DESCRIPTION
    Inicia el túnel Pinggy con el comando optimizado
    Uso: .\start_tunnel.ps1
#>

# Configuración
$token = "Fm4hH7kZ8sz+force"
$host_server = "free.pinggy.io"
$local_port = 8501
$remote_port = 443

function Show-Banner {
    Write-Host "`n╔════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║              🌐 CLIMAPI DASHBOARD - PINGGY.IO TUNNEL                        ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
}

function Show-Menu {
    Write-Host "📊 OPCIONES:" -ForegroundColor Yellow
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  1. 🚀 Iniciar Túnel Pinggy (en esta terminal)" -ForegroundColor Cyan
    Write-Host "  2. 📊 Iniciar Dashboard Streamlit" -ForegroundColor Cyan
    Write-Host "  3. 🎯 Túnel + Dashboard (instrucciones para 2 terminales)" -ForegroundColor Cyan
    Write-Host "  4. ⚙️  Ver Comando Pinggy Completo" -ForegroundColor Cyan
    Write-Host "  5. 🔑 Ver Configuración" -ForegroundColor Cyan
    Write-Host "  6. 📖 Ver Documentación" -ForegroundColor Cyan
    Write-Host "  7. ❌ Salir" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    Write-Host ""
}

function Start-Tunnel {
    Write-Host ""
    Write-Host "🌐 Iniciando túnel Pinggy..." -ForegroundColor Green
    Write-Host ""
    Write-Host "🔗 Token:      $token" -ForegroundColor Magenta
    Write-Host "🚪 Puerto:     $local_port → $remote_port (HTTPS)" -ForegroundColor Magenta
    Write-Host "🌐 Servidor:   $host_server" -ForegroundColor Magenta
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    Write-Host ""
    Write-Host "📡 Comando:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "pinggy.exe -p 443 -R0:127.0.0.1:$local_port -o StrictHostKeyChecking=no -o ServerAliveInterval=30 $token@$host_server" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    Write-Host ""
    Write-Host "⏳ Conectando..." -ForegroundColor Yellow
    Write-Host ""
    
    # Intentar ejecutar pinggy.exe
    $command = "pinggy.exe -p 443 -R0:127.0.0.1:$local_port -o StrictHostKeyChecking=no -o ServerAliveInterval=30 $token@$host_server"
    
    try {
        Invoke-Expression $command
    }
    catch {
        Write-Host ""
        Write-Host "⚠️  Error: $_" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "💡 Soluciones:" -ForegroundColor Yellow
        Write-Host "  1. Descargar pinggy.exe desde: https://pinggy.io/" -ForegroundColor Gray
        Write-Host "  2. Asegúrate de que pinggy.exe esté en tu PATH" -ForegroundColor Gray
        Write-Host "  3. O colócalo en este directorio y renómbralo a pinggy.exe" -ForegroundColor Gray
        Write-Host ""
        Write-Host "  Alternativa: Usar SSH" -ForegroundColor Gray
        Write-Host "  ssh -R 0:localhost:$local_port $host_server" -ForegroundColor Gray
        Write-Host ""
    }
}

function Start-Dashboard {
    Write-Host ""
    Write-Host "🎨 Iniciando Dashboard Streamlit..." -ForegroundColor Green
    Write-Host ""
    Write-Host "📍 URL Local: http://localhost:$local_port" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "⏳ Cargando..." -ForegroundColor Yellow
    Write-Host ""
    
    & ".venv\Scripts\streamlit.exe" run "dashboard/app.py"
}

function Show-BothInstructions {
    Write-Host ""
    Write-Host "🚀 INICIANDO TÚNEL + DASHBOARD" -ForegroundColor Green
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Este script inicia el TÚNEL en esta terminal." -ForegroundColor Yellow
    Write-Host "Para iniciar el DASHBOARD, abre OTRA terminal y ejecuta:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  .venv\Scripts\streamlit.exe run dashboard/app.py" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "O usa esta terminal después de finalizar el túnel." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    Write-Host ""
    
    Read-Host "Presiona Enter para iniciar el túnel..."
    Start-Tunnel
}

function Show-Command {
    Write-Host ""
    Write-Host "📋 COMANDO PINGGY COMPLETO" -ForegroundColor Green
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    Write-Host ""
    Write-Host "pinggy.exe -p 443 -R0:127.0.0.1:8501 -o StrictHostKeyChecking=no -o ServerAliveInterval=30 Fm4hH7kZ8sz+force@free.pinggy.io" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📝 Parámetros:" -ForegroundColor Yellow
    Write-Host "  -p 443                           Puerto HTTPS" -ForegroundColor Gray
    Write-Host "  -R0:127.0.0.1:8501              Reverse tunnel (local)" -ForegroundColor Gray
    Write-Host "  -o StrictHostKeyChecking=no     Sin verificación SSH" -ForegroundColor Gray
    Write-Host "  -o ServerAliveInterval=30       Keep-alive (segundos)" -ForegroundColor Gray
    Write-Host "  Fm4hH7kZ8sz+force@free.pinggy.io  Token + Host" -ForegroundColor Gray
    Write-Host ""
}

function Show-Config {
    Write-Host ""
    Write-Host "⚙️  CONFIGURACIÓN" -ForegroundColor Green
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  🔑 Token:           $token" -ForegroundColor Cyan
    Write-Host "  🌐 Host:            $host_server" -ForegroundColor Cyan
    Write-Host "  🚪 Puerto Local:    $local_port (HTTP)" -ForegroundColor Cyan
    Write-Host "  🚪 Puerto Remoto:   $remote_port (HTTPS)" -ForegroundColor Cyan
    Write-Host "  🔗 URL Pública:     https://Fm4hH7kZ8sz.free.pinggy.io" -ForegroundColor Cyan
    Write-Host ""
}

function Show-Documentation {
    Write-Host ""
    Write-Host "📚 DOCUMENTACIÓN" -ForegroundColor Green
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  📖 START_PINGGY.md              Inicio rápido (3 pasos)" -ForegroundColor Cyan
    Write-Host "  📖 PINGGY_COMMAND.md            Detalles del comando" -ForegroundColor Cyan
    Write-Host "  📖 PINGGY_GUIDE.md              Documentación completa" -ForegroundColor Cyan
    Write-Host "  📖 PINGGY_SETUP_COMPLETE.md     Configuración avanzada" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "⭐ Recomendación: Leer PINGGY_COMMAND.md para entender el comando" -ForegroundColor Yellow
    Write-Host ""
}

# Main Loop
do {
    Show-Banner
    Show-Menu
    
    $choice = Read-Host "Selecciona (1-7)"
    
    switch ($choice) {
        "1" {
            Start-Tunnel
        }
        "2" {
            Start-Dashboard
        }
        "3" {
            Show-BothInstructions
        }
        "4" {
            Show-Command
        }
        "5" {
            Show-Config
        }
        "6" {
            Show-Documentation
        }
        "7" {
            Write-Host ""
            Write-Host "👋 Hasta luego!" -ForegroundColor Green
            Write-Host ""
            exit 0
        }
        default {
            Write-Host ""
            Write-Host "❌ Opción no válida. Por favor selecciona 1-7." -ForegroundColor Red
            Write-Host ""
            Start-Sleep -Seconds 2
        }
    }
} while ($true)
