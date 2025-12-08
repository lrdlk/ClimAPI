# 🚀 INICIO INMEDIATO - Pinggy.io para ClimAPI

## ⚡ En 3 Pasos (2 Minutos)

### Paso 1️⃣: Opción A - Script (Recomendado)
```powershell
python pinggy_direct.py
```

Selecciona **opción 1 o 2**

### Paso 1️⃣: Opción B - Comando Directo
```powershell
pinggy.exe -p 443 -R0:127.0.0.1:8501 -o StrictHostKeyChecking=no -o ServerAliveInterval=30 Fm4hH7kZ8sz+force@free.pinggy.io
```

### Paso 2️⃣: Abrir Nueva Terminal
```powershell
.venv\Scripts\streamlit.exe run dashboard/app.py
```

### Paso 3️⃣: Compartir URL
```
Output en Terminal 1:
Port 8501 is forwarded to https://Fm4hH7kZ8sz.free.pinggy.io

✅ ¡Usa esta URL!
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
