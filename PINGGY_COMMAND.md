# 🚀 PINGGY.EXE - Uso Directo

## Tu Comando

```powershell
pinggy.exe -p 443 -R0:127.0.0.1:80 -L4300:127.0.0.1:4300 -o StrictHostKeyChecking=no -o ServerAliveInterval=30 Fm4hH7kZ8sz+force@free.pinggy.io
```

## 📝 Explicación de Parámetros

| Parámetro | Significado | Tu Valor |
|-----------|-------------|---------|
| `-p 443` | Puerto HTTPS | 443 (seguro) |
| `-R0:127.0.0.1:80` | Forward reverso | Túnel remoto → local 80 |
| `-L4300:127.0.0.1:4300` | Forward local | Local 4300 → remoto 4300 |
| `-o StrictHostKeyChecking=no` | Sin verificación SSH | Conexión automática |
| `-o ServerAliveInterval=30` | Keep-alive (segundos) | Mantiene conexión activa |
| Token | Autenticación | `Fm4hH7kZ8sz+force` |
| Host | Servidor Pinggy | `free.pinggy.io` |

## 🎯 Para ClimAPI (Dashboard en Puerto 8501)

Modifica el comando:

```powershell
pinggy.exe -p 443 -R0:127.0.0.1:8501 -o StrictHostKeyChecking=no -o ServerAliveInterval=30 Fm4hH7kZ8sz+force@free.pinggy.io
```

## 🚀 Uso Inmediato

### Opción 1: Terminal Directa
```powershell
# Terminal 1: Iniciar túnel
pinggy.exe -p 443 -R0:127.0.0.1:8501 -o StrictHostKeyChecking=no -o ServerAliveInterval=30 Fm4hH7kZ8sz+force@free.pinggy.io

# Terminal 2: Iniciar dashboard
.venv\Scripts\streamlit.exe run dashboard/app.py
```

### Opción 2: Script Automatizado
```powershell
python pinggy_direct.py
# → Seleccionar opción 1 o 2
```

### Opción 3: Script Original
```powershell
python pinggy_installer.py
# → Ya actualizado para usar pinggy.exe
```

## 📊 Output Esperado

```
Connecting to Pinggy...
SSH-2.0-OpenSSH_8.0

Port 8501 is forwarded to https://Fm4hH7kZ8sz.free.pinggy.io
```

## 🔐 Seguridad

- ✅ Token único: `Fm4hH7kZ8sz+force`
- ✅ HTTPS automático (puerto 443)
- ✅ Keep-alive cada 30 segundos (evita desconexiones)
- ✅ Sin verificación SSH (más rápido, token autentica)

## 🐛 Solución de Problemas

### "pinggy.exe not found"
```powershell
# Descargar pinggy.exe
# Desde: https://pinggy.io/

# O agregar a PATH:
$env:PATH += ";C:\ruta\a\pinggy"

# O usar ruta completa:
C:\ruta\a\pinggy.exe -p 443 ...
```

### "Connection refused"
```powershell
# Verificar que dashboard esté en puerto 8501
# Terminal 2: .venv\Scripts\streamlit.exe run dashboard/app.py
```

### "Timeout"
```powershell
# Reintentar:
pinggy.exe -p 443 -R0:127.0.0.1:8501 -o StrictHostKeyChecking=no -o ServerAliveInterval=30 Fm4hH7kZ8sz+force@free.pinggy.io
```

## ✨ Parámetros Explicados Detallado

### `-p 443`
Puerto HTTPS de salida. ClimAPI usará:
- Local: `http://localhost:8501`
- Remoto: `https://Fm4hH7kZ8sz.free.pinggy.io`

### `-R0:127.0.0.1:8501`
- `R` = Reverse (túnel remoto)
- `0` = Asignar puerto automático (Pinggy elige)
- `127.0.0.1:8501` = Tu dashboard local

Resultado:
```
tu-pc:8501 ←→ (SSH Tunnel) ←→ free.pinggy.io:443
```

### `-L4300:127.0.0.1:4300`
Opcional. Para si necesitas forwarding local también:
- Local puerto 4300 ↔ Remoto puerto 4300

### `-o StrictHostKeyChecking=no`
No preguntar "¿Confías en este servidor?" (más rápido)

### `-o ServerAliveInterval=30`
Mantiene la conexión viva enviando pings cada 30 segundos.
Evita que el ISP/firewall cierre la conexión inactiva.

## 📈 Monitoreo

Una vez conectado:
- 🌐 [Dashboard Pinggy](https://pinggy.io/dashboard)
- 📊 Ver tráfico, conexiones, historial
- 🔐 Gestionar tokens

## 💾 Guardar Comando en Batch Script

Para no escribirlo cada vez:

**`start_tunnel.bat`:**
```batch
@echo off
cd /d "%~dp0"
pinggy.exe -p 443 -R0:127.0.0.1:8501 -o StrictHostKeyChecking=no -o ServerAliveInterval=30 Fm4hH7kZ8sz+force@free.pinggy.io
pause
```

Uso:
```powershell
.\start_tunnel.bat
```

## 🎓 Próximos Pasos

1. **Terminal 1:** Ejecutar comando pinggy.exe
2. **Terminal 2:** `.venv\Scripts\streamlit.exe run dashboard/app.py`
3. **Copiar URL** de salida pinggy
4. **Compartir** con equipo
5. **Ver dashboard** en `https://Fm4hH7kZ8sz.free.pinggy.io`

## 📚 Referencia Rápida

```powershell
# Comando completo para ClimAPI
pinggy.exe -p 443 -R0:127.0.0.1:8501 -o StrictHostKeyChecking=no -o ServerAliveInterval=30 Fm4hH7kZ8sz+force@free.pinggy.io

# Alternativa: Con SSH
ssh -R 0:localhost:8501 Fm4hH7kZ8sz+force@free.pinggy.io

# Verificar conexión
curl https://Fm4hH7kZ8sz.free.pinggy.io

# Logs en tiempo real
pinggy.exe -p 443 -R0:127.0.0.1:8501 -v Fm4hH7kZ8sz+force@free.pinggy.io
```

---

**¡Tu túnel está configurado!** 🎉

Usa `python pinggy_direct.py` para interfaz amigable o ejecuta el comando directamente en terminal.
