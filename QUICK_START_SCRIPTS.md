# ⚡ CÓMO EJECUTAR LOS SCRIPTS - Guía Rápida

## 🔴 PROBLEMA

```powershell
start_tunnel.bat: The term 'start_tunnel.bat' is not recognized...
```

PowerShell no ejecuta archivos del directorio actual por defecto. Necesitas el prefijo `.\`

## ✅ SOLUCIÓN RECOMENDADA (SÚPER SIMPLE)

```powershell
.\run-tunnel.ps1
```

**Esto es lo más simple posible:**
- ✅ Una línea
- ✅ Nativo a PowerShell  
- ✅ Sin menú (solo inicia túnel)
- ✅ Output bonito
- ✅ Presiona Ctrl+C para detener

---

## 📋 OTRAS OPCIONES

### Opción 1: Script PowerShell con Menú (Más Controles)

```powershell
.\start_tunnel.ps1
```

**Ventajas:**
- Menú interactivo (7 opciones)
- Ver configuración
- Ver documentación
- Iniciar dashboard desde aquí

### Opción 2: Batch Script (Si prefieres CMD)

```powershell
.\start_tunnel.bat
```

O con cmd.exe:
```cmd
start_tunnel.bat
```

### Opción 3: Script Python (Alternativa)

```powershell
python pinggy_direct.py
```

### Opción 4: Comando Directo (Expert)

```powershell
pinggy.exe -p 443 -R0:127.0.0.1:8501 -o StrictHostKeyChecking=no -o ServerAliveInterval=30 Fm4hH7kZ8sz+force@free.pinggy.io
```

---

## 🚀 GUÍA PASO A PASO (QUICK START)

### Paso 1: Abre PowerShell en el Directorio del Proyecto

```powershell
cd "e:\C0D3\Python\Jupyter\ClimAPI"
```

### Paso 2: Ejecuta el Script Más Simple

```powershell
.\run-tunnel.ps1
```

**Output que verás:**
```
╔════════════════════════════════════════════════════════════════════════════╗
║              🌐 CLIMAPI DASHBOARD - PINGGY.IO TUNNEL                      ║
╚════════════════════════════════════════════════════════════════════════════╝

⏳ Iniciando túnel...

📊 Dashboard Local:
   🔗 http://localhost:8501

🌐 Dashboard Remoto (HTTPS):
   🔗 https://Fm4hH7kZ8sz.free.pinggy.io
```

### Paso 3: Abre Otra Terminal (Nueva)

```powershell
# En nueva terminal:
cd "e:\C0D3\Python\Jupyter\ClimAPI"
.venv\Scripts\streamlit.exe run dashboard/app.py
```

### Paso 4: ¡Listo!

Tu dashboard está accesible en:
- Local: `http://localhost:8501`
- Remoto: `https://Fm4hH7kZ8sz.free.pinggy.io`

---

## 🎯 RESUMEN DE SCRIPTS

| Script | Complejidad | Uso |
|--------|-------------|-----|
| `.\run-tunnel.ps1` | ⭐ **SIMPLE** | ✅ **RECOMENDADO** |
| `.\start_tunnel.ps1` | ⭐⭐⭐ Medio | Menú completo |
| `.\start_tunnel.bat` | ⭐⭐ Básico | Alternativa CMD |
| `python pinggy_direct.py` | ⭐⭐ Básico | Menú Python |

---

## ❓ ¿POR QUÉ FALLA?

```powershell
# ❌ FALLA - Ruta relativa
start_tunnel.bat

# ✅ FUNCIONA - Con .\
.\start_tunnel.bat

# ✅ FUNCIONA - Ruta completa
C:\ruta\completa\start_tunnel.bat

# ✅ FUNCIONA - Desde cmd.exe
cmd /c start_tunnel.bat
```

**PowerShell por seguridad no ejecuta comandos del directorio actual sin el prefijo `.\`**

---

## 💡 RECOMENDACIONES

### Para Uso Frecuente - Crear Alias

Crea un alias en tu perfil de PowerShell:

```powershell
# Abre tu perfil:
notepad $PROFILE

# Agrega esta línea:
Set-Alias -Name tunnel -Value ".\run-tunnel.ps1"

# Luego guarda y recarga PowerShell

# Ahora puedes usar:
tunnel
```

### Para Máxima Comodidad - Desktop Shortcut

Coloca un acceso directo en tu escritorio:

```powershell
$WshShell = New-Object -ComObject WScript.Shell
$Lnk = $WshShell.CreateShortCut("$env:USERPROFILE\Desktop\ClimAPI Tunnel.lnk")
$Lnk.TargetPath = "powershell.exe"
$Lnk.Arguments = "-NoExit -File `"e:\C0D3\Python\Jupyter\ClimAPI\run-tunnel.ps1`""
$Lnk.WorkingDirectory = "e:\C0D3\Python\Jupyter\ClimAPI"
$Lnk.IconLocation = "powershell.exe,0"
$Lnk.Save()
```

O simplemente crea un archivo `run_tunnel.cmd`:

```batch
@echo off
cd /d "e:\C0D3\Python\Jupyter\ClimAPI"
powershell.exe -NoExit -File "run-tunnel.ps1"
```

Doble clic = ¡Listo!

---

## 📚 ARCHIVOS DISPONIBLES

| Archivo | Tipo | Complejidad | Recomendado |
|---------|------|-------------|------------|
| `run-tunnel.ps1` | PowerShell | ⭐ Simple | ✅ **SÍ** |
| `start_tunnel.ps1` | PowerShell | ⭐⭐⭐ Menú | Para más opciones |
| `start_tunnel.bat` | Batch | ⭐⭐ Básico | Alternativa |
| `pinggy_direct.py` | Python | ⭐⭐ Básico | Si prefieres Python |

---

## ✅ VERIFICACIÓN

Una vez ejecutado, deberías ver:

```
╔════════════════════════════════════════════════════════════════════════════╗
║              🌐 CLIMAPI DASHBOARD - PINGGY.IO TUNNEL                      ║
╚════════════════════════════════════════════════════════════════════════════╝

⏳ Iniciando túnel...

📊 Dashboard Local:
   🔗 http://localhost:8501

🌐 Dashboard Remoto (HTTPS):
   🔗 https://Fm4hH7kZ8sz.free.pinggy.io

[Aquí verás logs de pinggy.exe]
```

---

## 🎉 ¡LISTO!

Ahora ejecuta en otra terminal:

```powershell
.venv\Scripts\streamlit.exe run dashboard/app.py
```

Y accede a:
- **Local:** http://localhost:8501
- **Remoto:** https://Fm4hH7kZ8sz.free.pinggy.io

---

## 📞 AYUDA

**Script PowerShell no funciona:**
```powershell
# Permitir ejecución de scripts:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**pinggy.exe no encontrado:**
```
Descargar desde: https://pinggy.io/
Agregar a PATH o colocar en este directorio
```

**Dashboard no inicia:**
```powershell
# Verificar que las dependencias estén instaladas:
pip install -r requirements.txt
```

**¿Ves el error "The term 'run-tunnel.ps1' is not recognized"?**
```powershell
# Usa el prefijo ./
.\run-tunnel.ps1
```

---

## 🎯 FLUJO RECOMENDADO

```
1. cd "e:\C0D3\Python\Jupyter\ClimAPI"
2. .\run-tunnel.ps1                                    [Terminal 1]
3. (Abre nueva terminal PowerShell)
4. cd "e:\C0D3\Python\Jupyter\ClimAPI"
5. .venv\Scripts\streamlit.exe run dashboard/app.py  [Terminal 2]
6. Accede a: https://Fm4hH7kZ8sz.free.pinggy.io      [Navegador]
```

---

**¡Usa `.\run-tunnel.ps1` y listo! 🚀**

