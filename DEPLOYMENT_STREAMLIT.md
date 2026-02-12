# 📦 Guía de Despliegue en Streamlit Cloud

## 🎯 Resumen

Esta guía explica cómo desplegar CLIMAPI Dashboard en Streamlit Cloud.

## ⚠️ Problemas Identificados y Soluciones

### 1. **Dependencias de Sistema Faltantes**

**Problema:** Paquetes científicos como `arm-pyart`, `wradlib`, `netCDF4` requieren bibliotecas del sistema para compilar.

**Solución:** Se creó el archivo `packages.txt` que Streamlit Cloud usa para instalar dependencias del sistema:
```
gcc
g++
gfortran
libhdf5-dev
libnetcdf-dev
libgeos-dev
libproj-dev
```

### 2. **Configuración de Streamlit Faltante**

**Problema:** Sin configuración `.streamlit/config.toml`, Streamlit usa valores predeterminados.

**Solución:** Se creó `.streamlit/config.toml` con configuración optimizada para despliegue en la nube.

### 3. **Variables de Entorno**

**Problema:** Las APIs requieren claves que no pueden estar en el código.

**Solución:** Configurar en Streamlit Cloud → Settings → Secrets:

```toml
# Copiar el contenido de .streamlit/secrets.toml.example
METEOBLUE_API_KEY = "tu_api_key_real"
METEOBLUE_SHARED_SECRET = "tu_shared_secret_real"
METEOSOURCE_API_KEY = "tu_api_key_real"
OPENWEATHER_API_KEY = "tu_api_key_real"
```

### 4. **Archivos de Caché en el Repositorio**

**Problema:** Archivos `.cache.sqlite` y otros cachés estaban versionados.

**Solución:** Se actualizó `.gitignore` y se removieron del índice de git.

## 🚀 Pasos para Desplegar

### 1. Preparar el Repositorio

```bash
# Asegurarse de que todos los archivos estén actualizados
git pull origin main

# Verificar que existan los archivos necesarios:
# - requirements.txt
# - packages.txt
# - .streamlit/config.toml
# - dashboard.py
```

### 2. Conectar a Streamlit Cloud

1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Inicia sesión con tu cuenta de GitHub
3. Haz clic en "New app"
4. Selecciona:
   - Repository: `lrdlk/ClimAPI`
   - Branch: `main` (o la rama que desees)
   - Main file path: `dashboard.py`

### 3. Configurar Secrets

1. En el dashboard de Streamlit Cloud, ve a tu app
2. Haz clic en "Settings" → "Secrets"
3. Copia el contenido de `.streamlit/secrets.toml.example`
4. Reemplaza los valores de ejemplo con tus claves API reales
5. Guarda los cambios

### 4. Configurar Opciones Avanzadas (Opcional)

En "Settings" → "Advanced settings":
- **Python version:** 3.9+ (recomendado 3.11)
- **Memory:** Al menos 1GB (recomendado 2GB debido a paquetes científicos)

### 5. Deploy

Haz clic en "Deploy!" y espera a que se complete la instalación.

## ⏱️ Tiempo de Despliegue Esperado

- **Primera vez:** 15-20 minutos (compilación de paquetes científicos)
- **Redespliegues:** 5-10 minutos (usa caché cuando es posible)

## 🐛 Solución de Problemas Comunes

### Error: "Could not build wheels for xxx"

**Causa:** Falta alguna dependencia del sistema.

**Solución:** Verificar que `packages.txt` incluya todas las bibliotecas necesarias.

### Error: "ModuleNotFoundError"

**Causa:** Paquete faltante en `requirements.txt`.

**Solución:** Añadir el paquete faltante a `requirements.txt` y hacer commit.

### Error: "Permission denied" o "Unable to access data/"

**Causa:** Streamlit Cloud tiene sistema de archivos de solo lectura excepto `/tmp`.

**Solución:** El dashboard debe configurarse para no escribir en `data/` en producción. Las funciones de descarga de datos deben deshabilitarse en la nube.

### App muy lenta o se queda sin memoria

**Causa:** Paquetes científicos pesados (arm-pyart, wradlib) consumen mucha RAM.

**Solución:** 
1. Solicitar más memoria en configuración avanzada
2. Considerar crear un `requirements-streamlit.txt` más ligero sin los paquetes de radar si no se usan en el dashboard

## 📋 Checklist Pre-Despliegue

- [ ] `requirements.txt` está actualizado
- [ ] `packages.txt` existe y tiene todas las dependencias del sistema
- [ ] `.streamlit/config.toml` existe
- [ ] `.gitignore` excluye archivos de caché y `.env`
- [ ] Archivos de caché removidos del repositorio
- [ ] Variables de entorno preparadas para copiar en Secrets
- [ ] Dashboard probado localmente: `streamlit run dashboard.py`

## 🔍 Verificación Local

Antes de desplegar, prueba localmente:

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar dashboard
streamlit run dashboard.py
```

El dashboard debería abrir en `http://localhost:8501`

## 📝 Notas Importantes

1. **APIs Opcionales:** El dashboard debe funcionar incluso si no todas las APIs están configuradas
2. **Datos Históricos:** Los datos en `data/` no estarán disponibles en Streamlit Cloud (son muy pesados)
3. **Performance:** La primera carga puede ser lenta debido a las importaciones de paquetes científicos

## 🔗 Enlaces Útiles

- [Documentación de Streamlit Cloud](https://docs.streamlit.io/streamlit-community-cloud)
- [Configuración de Secrets](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
- [Límites y recursos](https://docs.streamlit.io/streamlit-community-cloud/manage-your-app/app-resources-and-limits)
