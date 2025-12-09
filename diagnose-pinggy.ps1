#!/usr/bin/env powershell
# ============================================================================
# ClimAPI - Diagnóstico de Instalación de Pinggy
# ============================================================================
# Verifica dónde está pinggy.exe y cómo solucionarlo
# Uso: .\diagnose-pinggy.ps1
# ============================================================================

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                  🔍 DIAGNÓSTICO DE PINGGY - Windows                       ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# 1. Buscar pinggy.exe en ubicaciones comunes
Write-Host "⏳ Buscando pinggy.exe en tu sistema..." -ForegroundColor Yellow
$commonPaths = @(
    "$env:USERPROFILE\pinggy",
    "$env:USERPROFILE\pinggy.exe",
    "$env:USERPROFILE\Downloads\pinggy.exe",
    "$env:USERPROFILE\AppData\Local\pinggy.exe",
    "C:\pinggy.exe",
    "C:\Program Files\pinggy.exe",
    "C:\Program Files (x86)\pinggy.exe"
)

$pinggyLocation = $null

foreach ($path in $commonPaths) {
    if (Test-Path $path) {
        Write-Host "✅ Encontrado: $path" -ForegroundColor Green
        $pinggyLocation = $path
        break
    }
}

if (-not $pinggyLocation) {
    Write-Host "❌ No encontrado en ubicaciones comunes" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔎 Buscando en todo el sistema (esto puede tomar un momento)..." -ForegroundColor Yellow
    
    try {
        $result = Get-ChildItem -Path "C:\" -Filter "pinggy.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($result) {
            $pinggyLocation = $result.FullName
            Write-Host "✅ Encontrado: $pinggyLocation" -ForegroundColor Green
        }
    } catch {
        Write-Host "⚠️  Búsqueda en C:\ limitada por permisos" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "═════════════════════════════════════════════════════════════════════════════" -ForegroundColor DarkGray
Write-Host ""

if ($pinggyLocation) {
    Write-Host "📍 UBICACIÓN DE PINGGY ENCONTRADA" -ForegroundColor Green
    Write-Host ""
    Write-Host "Ruta completa:" -ForegroundColor Yellow
    Write-Host "  $pinggyLocation" -ForegroundColor Cyan
    Write-Host ""
    
    # Obtener información del archivo
    $fileInfo = Get-Item $pinggyLocation
    Write-Host "Tamaño: $([math]::Round($fileInfo.Length / 1MB, 2)) MB" -ForegroundColor Gray
    Write-Host "Última modificación: $($fileInfo.LastWriteTime)" -ForegroundColor Gray
    
    Write-Host ""
    Write-Host "🔧 OPCIONES PARA SOLUCIONARLO" -ForegroundColor Yellow
    Write-Host ""
    
    Write-Host "Opción 1: AGREGAR AL PATH (RECOMENDADO)" -ForegroundColor Green
    Write-Host "─────────────────────────────────────────────────────────────────────────"
    Write-Host ""
    
    # Extraer el directorio
    $pinggyDir = Split-Path $pinggyLocation
    Write-Host "Dirección del directorio:" -ForegroundColor Yellow
    Write-Host "  $pinggyDir" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Pasos a seguir:" -ForegroundColor Cyan
    Write-Host "  1. Click derecho en 'Este equipo' → Propiedades" -ForegroundColor Gray
    Write-Host "  2. Click en 'Configuración avanzada del sistema'" -ForegroundColor Gray
    Write-Host "  3. Click en 'Variables de entorno'" -ForegroundColor Gray
    Write-Host "  4. Click en 'Path' → 'Editar'" -ForegroundColor Gray
    Write-Host "  5. Click en 'Nuevo' y pega:" -ForegroundColor Gray
    Write-Host "     $pinggyDir" -ForegroundColor Cyan
    Write-Host "  6. Click 'Aceptar' y reinicia PowerShell" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "Opción 2: CREAR ALIAS EN POWERSHELL (RÁPIDO)" -ForegroundColor Green
    Write-Host "─────────────────────────────────────────────────────────────────────────"
    Write-Host ""
    Write-Host "Abre tu perfil de PowerShell:" -ForegroundColor Cyan
    Write-Host "  notepad `$PROFILE" -ForegroundColor White
    Write-Host ""
    Write-Host "Agrega esta línea:" -ForegroundColor Cyan
    Write-Host "  Set-Alias -Name pinggy -Value '$pinggyLocation'" -ForegroundColor Magenta
    Write-Host ""
    Write-Host "Guarda (Ctrl+S) y recarga PowerShell" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "Opción 3: USAR RUTA COMPLETA (INMEDIATO)" -ForegroundColor Green
    Write-Host "─────────────────────────────────────────────────────────────────────────"
    Write-Host ""
    Write-Host "En lugar de:" -ForegroundColor Yellow
    Write-Host "  pinggy.exe -p 443 -R0:127.0.0.1:8501 ..." -ForegroundColor Gray
    Write-Host ""
    Write-Host "Usa:" -ForegroundColor Yellow
    Write-Host "  '$pinggyLocation' -p 443 -R0:127.0.0.1:8501 ..." -ForegroundColor Magenta
    Write-Host ""
    
    Write-Host "═════════════════════════════════════════════════════════════════════════════" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "⚡ SOLUCIÓN RÁPIDA - Ejecuta esto ahora:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "PowerShell (recomendado):" -ForegroundColor Cyan
    Write-Host "  & '$pinggyLocation' -p 443 -R0:127.0.0.1:8501 -o StrictHostKeyChecking=no -o ServerAliveInterval=30 Fm4hH7kZ8sz+force@free.pinggy.io" -ForegroundColor White
    Write-Host ""
    
} else {
    Write-Host "❌ PINGGY NO ENCONTRADO EN EL SISTEMA" -ForegroundColor Red
    Write-Host ""
    Write-Host "📥 DESCARGAR E INSTALAR PINGGY" -ForegroundColor Yellow
    Write-Host "─────────────────────────────────────────────────────────────────────────"
    Write-Host ""
    Write-Host "1. Ve a: https://pinggy.io/" -ForegroundColor Cyan
    Write-Host "2. Descarga pinggy.exe para Windows" -ForegroundColor Cyan
    Write-Host "3. Elige dónde guardarlo:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "   Opción A: En un directorio como C:\pinggy\" -ForegroundColor Yellow
    Write-Host "   Opción B: En tu carpeta de proyecto (recomendado para desarrollo)" -ForegroundColor Yellow
    Write-Host "   Opción C: En C:\Program Files\pinggy\" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "4. Una vez descargado, agrega a PATH o usa con ruta completa" -ForegroundColor Cyan
    Write-Host ""
}

Write-Host ""
Write-Host "📚 DOCUMENTACIÓN RELACIONADA" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────────────────────────────────────────"
Write-Host "  • run-tunnel.ps1 - Script que usa pinggy.exe" -ForegroundColor Gray
Write-Host "  • PINGGY_COMMAND.md - Detalles técnicos" -ForegroundColor Gray
Write-Host "  • QUICK_START_SCRIPTS.md - Guía de scripts" -ForegroundColor Gray
Write-Host ""
