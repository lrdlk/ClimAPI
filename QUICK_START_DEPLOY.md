# 🚀 Inicio Rápido - Despliegue en Streamlit Cloud

## ⚡ Resumen Rápido

¿Quieres desplegar CLIMAPI Dashboard en Streamlit Cloud? Sigue estos pasos:

### 1️⃣ Preparación (5 minutos)

✅ El repositorio ya está listo con:
- ✅ `.streamlit/config.toml` - Configuración
- ✅ `packages.txt` - Dependencias del sistema  
- ✅ `requirements.txt` - Dependencias de Python
- ✅ `dashboard.py` - Aplicación principal

### 2️⃣ Desplegar (3 minutos)

1. **Ir a:** https://share.streamlit.io
2. **Login** con tu cuenta de GitHub
3. **Click:** "New app"
4. **Configurar:**
   - Repository: `lrdlk/ClimAPI`
   - Branch: `main`
   - Main file: `dashboard.py`
5. **Click:** "Deploy"

### 3️⃣ Configurar API Keys (2 minutos)

1. En tu app desplegada, click en **⚙️ Settings** → **Secrets**
2. Copiar el contenido de `.streamlit/secrets.toml.example`
3. Reemplazar `your_api_key_here` con tus claves reales
4. Guardar

### 4️⃣ Listo! 🎉

La app debería estar funcionando en:
```
https://[tu-app].streamlit.app
```

---

## ⏱️ Tiempo Total: ~10 minutos

- Preparación: Ya está hecho ✅
- Despliegue: ~15-20 min (primera vez, automático)
- Configuración: 2-5 min (manual)

---

## 📚 Documentación Completa

Para más detalles, consultar:

- **[DEPLOYMENT_STREAMLIT.md](DEPLOYMENT_STREAMLIT.md)** - Guía completa paso a paso
- **[INFORME_DESPLIEGUE_STREAMLIT.md](INFORME_DESPLIEGUE_STREAMLIT.md)** - Análisis técnico detallado

---

## ⚠️ Problemas Comunes

### "Could not build wheels"
- **Causa:** Falta `packages.txt`
- **Solución:** Ya está incluido en el repo ✅

### "Module not found"  
- **Causa:** Dependencia faltante
- **Solución:** Verificar `requirements.txt`

### "API key not found"
- **Causa:** Secrets no configurados
- **Solución:** Seguir paso 3️⃣

### App muy lenta
- **Causa:** Paquetes científicos pesados
- **Solución:** Normal en primera carga (cache después)

---

## 🎯 Siguiente Paso

👉 **[DESPLEGAR AHORA](https://share.streamlit.io)**

¿Preguntas? Ver [DEPLOYMENT_STREAMLIT.md](DEPLOYMENT_STREAMLIT.md)
