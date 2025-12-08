#!/usr/bin/env powershell
# ============================================================================
# ClimAPI - Verificación Rápida de Sistema
# ============================================================================
# Verifica que todos los scripts y dependencias estén listos
# Uso: .\verify-system.ps1
# ============================================================================

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                  🔍 VERIFICACIÓN DE SISTEMA - ClimAPI                     ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$checks = @()
$failed = 0
$passed = 0

# 1. Verificar Python
Write-Host "⏳ Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>$null
    if ($pythonVersion) {
        Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
        $passed++
    } else {
        Write-Host "❌ Python: No encontrado" -ForegroundColor Red
        $failed++
    }
} catch {
    Write-Host "❌ Python: No encontrado" -ForegroundColor Red
    $failed++
}

# 2. Verificar .venv
Write-Host "⏳ Verificando entorno virtual..." -ForegroundColor Yellow
if (Test-Path ".venv\Scripts\activate.ps1") {
    Write-Host "✅ .venv: Existe" -ForegroundColor Green
    $passed++
} else {
    Write-Host "❌ .venv: No encontrado" -ForegroundColor Red
    $failed++
}

# 3. Verificar Streamlit
Write-Host "⏳ Verificando Streamlit..." -ForegroundColor Yellow
if (Test-Path ".venv\Scripts\streamlit.exe") {
    Write-Host "✅ Streamlit: Instalado" -ForegroundColor Green
    $passed++
} else {
    Write-Host "❌ Streamlit: No instalado" -ForegroundColor Red
    $failed++
}

# 4. Verificar run-tunnel.ps1
Write-Host "⏳ Verificando run-tunnel.ps1..." -ForegroundColor Yellow
if (Test-Path "run-tunnel.ps1") {
    $size = (Get-Item "run-tunnel.ps1").Length
    Write-Host "✅ run-tunnel.ps1: Existe ($size bytes)" -ForegroundColor Green
    $passed++
} else {
    Write-Host "❌ run-tunnel.ps1: No encontrado" -ForegroundColor Red
    $failed++
}

# 5. Verificar start_tunnel.ps1
Write-Host "⏳ Verificando start_tunnel.ps1..." -ForegroundColor Yellow
if (Test-Path "start_tunnel.ps1") {
    $size = (Get-Item "start_tunnel.ps1").Length
    Write-Host "✅ start_tunnel.ps1: Existe ($size bytes)" -ForegroundColor Green
    $passed++
} else {
    Write-Host "❌ start_tunnel.ps1: No encontrado" -ForegroundColor Red
    $failed++
}

# 6. Verificar dashboard
Write-Host "⏳ Verificando dashboard..." -ForegroundColor Yellow
if (Test-Path "dashboard\app.py") {
    Write-Host "✅ Dashboard: Existe" -ForegroundColor Green
    $passed++
} else {
    Write-Host "❌ Dashboard: No encontrado" -ForegroundColor Red
    $failed++
}

# 7. Verificar .env
Write-Host "⏳ Verificando configuración (.env)..." -ForegroundColor Yellow
if (Test-Path ".env") {
    $content = Get-Content ".env" | Select-String "PINGGY_TOKEN" -Quiet
    if ($content) {
        Write-Host "✅ .env: Configurado con PINGGY_TOKEN" -ForegroundColor Green
        $passed++
    } else {
        Write-Host "⚠️  .env: Existe pero sin PINGGY_TOKEN" -ForegroundColor Yellow
        $failed++
    }
} else {
    Write-Host "⚠️  .env: No encontrado (creará uno automáticamente)" -ForegroundColor Yellow
}

# 8. Verificar PowerShell ejecutable
Write-Host "⏳ Verificando PowerShell..." -ForegroundColor Yellow
$psVersion = $PSVersionTable.PSVersion.Major
Write-Host "✅ PowerShell: v$psVersion" -ForegroundColor Green
$passed++

# 9. Verificar puerto 8501
Write-Host "⏳ Verificando puerto 8501..." -ForegroundColor Yellow
try {
    $port = Get-NetTCPConnection -LocalPort 8501 -ErrorAction SilentlyContinue
    if ($port) {
        Write-Host "⚠️  Puerto 8501: Ya está en uso" -ForegroundColor Yellow
    } else {
        Write-Host "✅ Puerto 8501: Disponible" -ForegroundColor Green
        $passed++
    }
} catch {
    Write-Host "✅ Puerto 8501: Disponible" -ForegroundColor Green
    $passed++
}

# Resumen
Write-Host ""
Write-Host "═════════════════════════════════════════════════════════════════════════════" -ForegroundColor DarkGray
Write-Host ""
Write-Host "📊 RESUMEN:" -ForegroundColor Cyan
Write-Host "   ✅ Pasadas: $passed" -ForegroundColor Green
Write-Host "   ❌ Fallidas: $failed" -ForegroundColor Red
Write-Host ""

if ($failed -eq 0) {
    Write-Host "🎉 ¡SISTEMA LISTO!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Puedes ejecutar:" -ForegroundColor Yellow
    Write-Host "  .\run-tunnel.ps1" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host "⚠️  Hay algunos elementos que revisar." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Por favor instala las dependencias:" -ForegroundColor Yellow
    Write-Host "  pip install -r requirements.txt" -ForegroundColor Cyan
    Write-Host ""
}

Write-Host "═════════════════════════════════════════════════════════════════════════════" -ForegroundColor DarkGray
Write-Host ""
Write-Host "📚 Para más detalles, consulta:" -ForegroundColor Yellow
Write-Host "   • DOCUMENTATION_GUIDE.md" -ForegroundColor Cyan
Write-Host "   • QUICK_FIX_POWERSHELL.txt" -ForegroundColor Cyan
Write-Host "   • POWERSHELL_ERROR_FIXED.md" -ForegroundColor Cyan
Write-Host ""
