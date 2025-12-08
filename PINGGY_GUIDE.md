# 🌐 Integración Pinggy.io - Guía Completa

## 📋 ¿Qué es Pinggy?

**Pinggy.io** es un servicio de túneling seguro que permite exponer aplicaciones locales a internet con HTTPS automático, sin configurar puertos ni DNS.

```
┌─────────────────────────────────────────────────────────────────┐
│  TU MÁQUINA LOCAL (privada)    →    INTERNET PÚBLICO (HTTPS)   │
│  http://localhost:8501        →    https://xxxx-xxxx.pinggy.io │
└─────────────────────────────────────────────────────────────────┘
```

## ✨ Ventajas

✅ **HTTPS Automático**: Tráfico cifrado sin certificados  
✅ **Sin Configuración**: No requiere puertos abiertos  
✅ **URL Pública**: Acceso desde cualquier dispositivo  
✅ **Seguro**: Token de acceso, no IP expuesta  
✅ **Gratuito**: Plan básico sin costo  
✅ **Fácil de Usar**: Un comando = Todo funcionando  

## 🚀 Instalación Rápida

### 1️⃣ Prerrequisitos

```powershell
# Verificar que tienes SSH (Windows 10+ lo tiene)
ssh -V

# Si no lo tienes, instalarlo desde:
# Configuración > Apps > Características Opcionales > OpenSSH Client
```

### 2️⃣ Obtener Token Pinggy (Opcional pero Recomendado)

#### Para Token Permanente:

1. Ve a [https://pinggy.io/](https://pinggy.io/)
2. Haz clic en **"Sign Up"** (gratis)
3. Crea cuenta con email o GitHub
4. Ve a **Settings** → **SSH Token**
5. Copia el token (ejemplo: `user_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx`)

#### Sin Token:

Puedes usar túneles temporales sin registrarte, pero la URL cambia cada vez.

### 3️⃣ Configurar Variable de Entorno (Recomendado)

**PowerShell:**
```powershell
# Temporal (solo esta sesión)
$env:PINGGY_TOKEN = 'tu_token_aqui'

# Permanente (todas las sesiones)
[Environment]::SetEnvironmentVariable("PINGGY_TOKEN", "tu_token_aqui", "User")
```

**O agregar a `.env`:**
```ini
# Pinggy Configuration
PINGGY_TOKEN=tu_token_aqui
```

### 4️⃣ Ejecutar

```powershell
# Opción A: Script interactivo
python run_with_pinggy.py

# Opción B: Directamente sin túnel
.venv\Scripts\streamlit.exe run dashboard/app.py

# Opción C: Solo túnel (manual)
ssh -R 0:localhost:8501 a.pinggy.io
```

## 📖 Uso Detallado

### Método 1: Script Interactivo (Recomendado)

```powershell
cd e:\C0D3\Python\Jupyter\ClimAPI
python run_with_pinggy.py
```

Verás un menú:
```
1. Lanzar Dashboard + Túnel Pinggy
2. Lanzar solo Dashboard
3. Configurar Token Pinggy
4. Salir
```

**Selecciona 1** para obtener URL pública automáticamente.

### Método 2: Túnel + Dashboard Separados

**Terminal 1 - Iniciar túnel:**
```powershell
ssh -R 0:localhost:8501 user_xxxxx@a.pinggy.io
```

Verás:
```
Port 8501 is forwarded to http://xxxx-xxxx.pinggy.io
```

**Terminal 2 - Iniciar dashboard:**
```powershell
cd e:\C0D3\Python\Jupyter\ClimAPI
.venv\Scripts\streamlit.exe run dashboard/app.py
```

### Método 3: Solo Dashboard Local

Sin Pinggy (solo para uso local):
```powershell
python run_dashboard.py
```

## 🔗 Acceso

### Con Pinggy Activo

**URL Pública:**
```
https://xxxx-xxxx.pinggy.io
```

Puedes:
- Compartir con colegas
- Acceder desde móvil
- Ver datos en tiempo real
- Sin VPN o puerto forwarding

**Localmente:**
```
http://localhost:8501
```

## 🔒 Seguridad

### Cómo Proteger tu Dashboard

**Opción 1: Token Pinggy (Incluido)**
- Solo tú tienes el token
- Acceso único a tu túnel
- URL privada

**Opción 2: Autenticación en Streamlit** (Recomendado)

Editar `dashboard/app.py`:
```python
import streamlit as st

# Agregar al inicio
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Dashboard Clima API")
    password = st.text_input("Contraseña:", type="password")
    
    if password == "tu_contraseña_segura":
        st.session_state.authenticated = True
        st.rerun()
    else:
        st.stop()

# El resto del código aquí...
```

**Opción 3: IP Whitelist en Pinggy**
- Configurar en [https://pinggy.io/](https://pinggy.io/) → Settings
- Solo IPs autorizadas pueden acceder

## 🐛 Solución de Problemas

### "ssh: command not found"
```powershell
# Windows: Instalar OpenSSH
# Configuración > Apps > Características Opcionales > OpenSSH Client
# Reiniciar PowerShell después
```

### "Connection refused"
```powershell
# Verificar que Streamlit esté corriendo
# Terminal 2: .venv\Scripts\streamlit.exe run dashboard/app.py
```

### "Bad hostname" / "Connection reset"
```powershell
# Reintentar:
ssh -R 0:localhost:8501 a.pinggy.io

# O con token:
ssh -R 0:localhost:8501 user_xxxxx@a.pinggy.io
```

### URL Caduca o Cambia

Si no tienes token, la URL es temporal:
- Solución: Registrarse en Pinggy y usar token permanente
- Editar: `run_with_pinggy.py` línea 49-55

### Latencia Alta

Pinggy puede tener 100-500ms de latencia:
- Normal para túneles de internet
- Dashboard todavía es usable
- Para producción, usar VPS dedicado

## 📊 Monitoreo

### Ver Conexiones Activas

En [https://pinggy.io/](https://pinggy.io/) Dashboard:
- Conexiones actuales
- Tráfico de datos
- Historial de accesos

### Logs del Túnel

```powershell
# El script muestra logs automáticos
# O revisar con:
ssh -R 0:localhost:8501 a.pinggy.io -v
```

## 🎯 Casos de Uso

### Desarrollo Colaborativo
```
1. Lanzar: python run_with_pinggy.py
2. Compartir URL: https://xxxx-xxxx.pinggy.io
3. Colegas acceden directamente
```

### Demostración en Cliente
```
1. Terminal 1: Túnel Pinggy
2. Terminal 2: Dashboard
3. Cliente accede desde su navegador
4. Ver datos en tiempo real
```

### Monitoreo Remoto
```
1. Dashboard corriendo 24/7
2. Acceder desde cualquier lugar
3. Ver gráficos y estadísticas
4. Recibir alertas (futuro)
```

### Mobile/Tablet
```
1. Túnel activo en laptop
2. Compartir URL
3. Ver dashboard en smartphone
4. Datos sincronizados
```

## 🔧 Configuración Avanzada

### Túnel Persistente (Systemd/Docker)

Para producción, considerar:

```bash
# Docker
docker run -p 8501:8501 streamlit:latest run dashboard/app.py
ssh -R 0:localhost:8501 token@a.pinggy.io

# Systemd (Linux)
[Unit]
Description=ClimAPI Dashboard with Pinggy

[Service]
ExecStart=bash -c "ssh -R 0:localhost:8501 token@a.pinggy.io"
Restart=always

[Install]
WantedBy=multi-user.target
```

### Custom Domain

Si necesitas dominio propio:
- Plan Pro de Pinggy (opcional)
- O usar Cloudflare Tunnel (alternativa)
- O desplegar en Heroku/Railway (más caro)

## 📚 Recursos

- 🌐 [Pinggy.io Official](https://pinggy.io/)
- 📖 [Documentación Pinggy](https://pinggy.io/docs/)
- 🎓 [SSH Tunneling Basics](https://www.ssh.com/ssh/tunneling/)
- 🐍 [Streamlit Docs](https://docs.streamlit.io/)

## 💡 Tips

1. **URL Pública Permanente**: Usa token Pinggy
2. **HTTPS Gratis**: Pinggy lo incluye automáticamente
3. **Múltiples Túneles**: Puedes abrir varios en diferentes puertos
4. **Rendimiento**: Dashboard sigue siendo local, solo exposición remota
5. **Seguridad**: Cambiar token cada 3 meses
6. **Monitoreo**: Revisar logs en Pinggy dashboard

## ✅ Próximos Pasos

```bash
# 1. Instalar OpenSSH (si no lo tienes)
# 2. Registrarse en https://pinggy.io (opcional)
# 3. Copiar token
# 4. Ejecutar:
python run_with_pinggy.py

# 5. Seleccionar opción 1
# 6. Compartir URL
# 7. ¡Listo!
```

---

**¿Necesitas ayuda?** Revisa los logs del script o prueba:
```powershell
ssh -v -R 0:localhost:8501 a.pinggy.io
```
