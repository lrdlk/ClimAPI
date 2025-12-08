# 🌐 Acceso Remoto ClimAPI con Pinggy.io

## ⚡ Inicio Rápido (30 segundos)

```powershell
# 1. Ejecutar instalador
python pinggy_installer.py

# 2. Seleccionar opción 1 (Pinggy)
# 3. Si es primera vez, pegar token de https://pinggy.io
# 4. ¡Listo! Compartir URL pública
```

## 🎯 ¿Qué Necesito?

✅ **Windows 10+** (tiene SSH incluido)  
✅ **Token Pinggy** (gratis en https://pinggy.io)  
✅ **Python** (ya tienes)  

Eso es todo. **Sin configuración de puertos ni certificados.**

## 📱 Resultado

### Antes
```
Local:  http://localhost:8501 (solo en tu máquina)
```

### Después
```
Local:  http://localhost:8501
Remoto: https://xxxx-xxxx.pinggy.io (accesible desde internet)
```

Cualquiera con la URL puede ver el dashboard en tiempo real.

## 🚀 Opciones

### Opción 1: Script Automático (Recomendado)
```powershell
python pinggy_installer.py
# Elige opción 1 y listo
```

### Opción 2: Script Interactivo (Avanzado)
```powershell
python run_with_pinggy.py
# Menú con más opciones
```

### Opción 3: Manual (Experto)
```powershell
# Terminal 1: Túnel
ssh -R 0:localhost:8501 a.pinggy.io

# Terminal 2: Dashboard
.venv\Scripts\streamlit.exe run dashboard/app.py
```

## 📖 Documentación Completa

Ver: [`PINGGY_GUIDE.md`](PINGGY_GUIDE.md)

Incluye:
- Instalación detallada
- Seguridad y autenticación
- Solución de problemas
- Casos de uso
- Monitoreo

## 💡 Casos de Uso Comunes

### Compartir con Colegas
```
1. python pinggy_installer.py
2. Opción 1
3. Copiar URL de salida
4. Enviar por WhatsApp/Email
5. ¡Ellos ven el dashboard en tiempo real!
```

### Demostración a Cliente
```
1. Túnel activo
2. Dashboard mostrando datos
3. Cliente ve en su navegador
4. Datos actualizados cada 15 segundos
```

### Monitoreo Remoto
```
1. Dashboard corriendo 24/7
2. Acceder desde móvil
3. Ver gráficos y alertas
4. Desde cualquier lugar
```

### Presentación Online
```
1. Compartir URL en Meet/Teams
2. Mostrar dashboard en tiempo real
3. Cambiar ubicaciones y ver datos
4. Funciona con internet lento
```

## ❓ Preguntas Frecuentes

**¿Qué es Pinggy?**
> Servicio que expone tu app local a internet con HTTPS y sin configuración.

**¿Es gratis?**
> Sí, plan básico es gratuito. Token permanente también gratis.

**¿Es seguro?**
> Sí, HTTPS cifrado + token de acceso. URL no es predecible.

**¿Qué latencia tiene?**
> 100-500ms normal. Dashboard sigue siendo usable.

**¿Se ve lento?**
> No, la latencia se nota poco en dashboards. Es principalmente de red.

**¿Puedo usarlo en producción?**
> Para usar interno/equipo sí. Para público masivo, considerar VPS.

**¿Cuánto tiempo dura el túnel?**
> Mientras el script esté corriendo. Ctrl+C para detenerlo.

**¿Qué pasa si cierro la terminal?**
> Se cierra el túnel. Ya no será accesible por URL.

**¿Puedo cambiar la URL?**
> Con token permanente no. Sin token, sí (cada vez nueva).

**¿Funcionará en Mac/Linux?**
> Sí, igual proceso. SSH viene incluido.

## 🔧 Requisitos Técnicos

```
Windows 10+         → SSH ya incluido ✅
OpenSSH Client      → Instalar si falta
Token Pinggy        → Gratis en https://pinggy.io
Dashboard activo    → .venv\Scripts\streamlit.exe run dashboard/app.py
```

## 🐛 Si Algo Falla

```powershell
# SSH no encontrado
# → Instalar: Configuración > Apps > Características Opcionales > OpenSSH Client

# "Connection refused"
# → Verificar: .venv\Scripts\streamlit.exe run dashboard/app.py

# "Bad hostname"
# → Reintentar: python pinggy_installer.py

# URL no funciona
# → Revisar: Túnel debe estar activo en otra terminal
```

## 📚 Siguientes Pasos

1. **Obtener Token Pinggy** (2 min)
   - https://pinggy.io/
   - Sign up (gratis)
   - Settings → SSH Token

2. **Ejecutar Installer** (1 min)
   ```powershell
   python pinggy_installer.py
   ```

3. **Seleccionar Opción 1** (30 seg)
   - Pegar token
   - Esperar URL

4. **Compartir URL** (inmediato)
   - Copiar URL pública
   - Enviar a colegas
   - ¡Ven dashboard en tiempo real!

## 🌟 Ventajas vs Alternativas

| Característica | Pinggy | VPN | Port Forward | Cloudflare |
|---|---|---|---|---|
| Setup | 1 min ⚡ | 5-10 min | 10 min+ | 5 min |
| HTTPS | Sí ✅ | Gratis | No ❌ | Sí ✅ |
| Configuración | Ninguna | Compleja | Media | Media |
| Costo | Gratis | Gratis | Gratis | Gratis |
| Movilidad | Alta | Media | Baja | Media |
| Velocidad | Buena | Excelente | Excelente | Buena |

**Mejor para:** Desarrollo rápido, demostraciones, colaboración

## 📞 Soporte

- 🔗 [Pinggy.io Official](https://pinggy.io/)
- 📖 [Documentación Completa](PINGGY_GUIDE.md)
- 🐛 [Issues](../../issues)

---

**¡Ahora sí! Tu dashboard es accesible desde internet con HTTPS.** 🎉
