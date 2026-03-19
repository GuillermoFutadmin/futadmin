# Bitácora de Despliegues y Versiones - FutAdmin

Este archivo registra los hitos importantes, nuevas funciones y despliegues (subidas) a producción en Railway.

---

## [2026-03-18] - Firma Digital del Tutor (Vuelo actual)
**Commit:** `f0c802f`
- **Función:** Implementación de firma digital interactiva para padres/tutores de jugadores menores de edad.
- **Frontend (Telegram Mini App):**
    - Canvas interactivo para dibujo táctil/mouse.
    - Validación doble: Checkbox legal + Firma obligatoria si es menor y sube foto.
    - Limpieza automática y carga rápida (PNG lightweight).
- **Backend:**
    - Modelo `Jugador` extendido con `firma_tutor_url`.
    - API de Arbitros actualizada para persistir la firma.
- **Base de Datos:** Migración ejecutada exitosamente agregando la columna `firma_tutor_url` en PostgreSQL.

---

## [2026-03-18] - Mejoras en Gestión Económica y Registro
**Commits:** `d9192c6` a `43ab826`
- **Registro:** Creación automática de `Inscripcion` y `Pago` al enrolar equipos vía scripts de carga masiva.
- **Admin:** Nueva ruta de diagnóstico de base de datos (`/api/debug/db`).
- **Infraestructura:** Optimización de sedes compartidas (Arena FutAdmin Central) y aislamiento administrativo por liga.

---

## [2026-03-18] - Optimización de Imágenes y Almacenamiento
**Commits:** `1d065b6` a `6a5c16c`
- **Imágenes:** Compresión automática en el cliente (max 800px, 70% calidad) antes de subir al servidor. Reduce consumo de datos y espacio.
- **Servidor:** Configuración de volumen persistente en Railway para que las fotos no se borren al reiniciar la app.

---

## [Previos] - Cimientos de la Telegram Mini App
- Integración con la API de Telegram.
- Roster de equipos, visualización de torneos y pagos básicos.
- Sistema de roles (Admin, Dueño, Arbitro, etc.).
