# 🚀 INICIO INMEDIATO - Pinggy.io para ClimAPI

## ⚡ En 3 Pasos (2 Minutos)

### Paso 1️⃣: Ejecutar Instalador
```powershell
python pinggy_installer.py
```

### Paso 2️⃣: Seleccionar Opción 1
```
¿Qué deseas hacer?

1. 🚀 Iniciar Dashboard con Pinggy (acceso público HTTPS)
2. 🔐 Configurar/cambiar Token Pinggy
3. 📊 Iniciar Dashboard solo local
4. ❌ Salir

Selecciona (1-4): 1
```

### Paso 3️⃣: Esperar la URL Pública
```
🌐 INICIANDO TÚNEL PINGGY.IO
⏳ Iniciando túnel...
⏳ Exponiendo puerto 8501 a través de Pinggy
   Esperando URL pública...

[Pinggy] Port 8501 is forwarded to https://xxxx-xxxx.pinggy.io

═══════════════════════════════════════════════════════════════════════

✅ TÚNEL ACTIVO

🔗 URL Pública (HTTPS):
   https://xxxx-xxxx.pinggy.io

📱 Acceso:
   • Desde internet: https://xxxx-xxxx.pinggy.io
   • Localmente: http://localhost:8501

═══════════════════════════════════════════════════════════════════════
```

## ✨ ¡Listo!

Ahora puedes:
- ✅ Compartir la URL con colegas
- ✅ Acceder desde cualquier dispositivo
- ✅ Ver datos en tiempo real
- ✅ Usando HTTPS seguro

## 🎯 Próximo: Obtener Token Permanente (Opcional)

Si quieres que la URL sea siempre la misma:

1. Ve a https://pinggy.io/
2. Crea cuenta (gratis)
3. Settings → SSH Token
4. Copia tu token
5. Ejecuta: `python pinggy_installer.py` → Opción 2

**Listo! Próxima vez la URL será igual.**

## 📚 Documentación

- 📖 [`PINGGY_QUICKSTART.md`](PINGGY_QUICKSTART.md) - Guía rápida
- 📘 [`PINGGY_GUIDE.md`](PINGGY_GUIDE.md) - Documentación completa
- 🏗️ [`PINGGY_INTEGRATION.md`](PINGGY_INTEGRATION.md) - Arquitectura

## ❓ ¿Preguntas?

**¿Qué es Pinggy?**
> Servicio que expone apps locales a internet con HTTPS, sin configuración.

**¿Es gratis?**
> Sí, totalmente gratis.

**¿Es seguro?**
> Sí, HTTPS + SSH + Token.

**¿Puedo usar sin token?**
> Sí, pero la URL cambia cada vez. Con token es permanente.

**¿Funciona en móvil?**
> Sí, desde cualquier navegador con internet.

## 🐛 Si Algo Falla

```powershell
# Verificar instalación
python verify_pinggy.py

# SSH no funciona
# → Configuración > Apps > Características Opcionales > OpenSSH Client

# Dashboard no funciona
# → Ejecutar en otra terminal: .venv\Scripts\streamlit.exe run dashboard/app.py
```

---

**¡A por ello!** 🎉

```powershell
python pinggy_installer.py
```
