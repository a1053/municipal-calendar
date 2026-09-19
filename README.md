# CSD Municipal — Calendario 1.0

Sistema autoactualizable para CSD Municipal. Mantiene una base SQLite, sincroniza el calendario oficial de Liga Nacional, aplica comunicados oficiales de reprogramación, genera un feed iCalendar y lo publica con GitHub Pages.

## Qué hace

- Identificador (`UID`) estable por partido para evitar duplicados.
- `SEQUENCE` aumenta cuando cambia un evento.
- Historial de cambios en SQLite.
- Fuente primaria: Liga Nacional de Fútbol de Guatemala.
- `overrides.json` para comunicados oficiales que aún no aparecen reflejados en la tabla web.
- Feed: `public/municipal.ics`.
- GitHub Actions cada 30 minutos + ejecución manual.
- Publicación automática mediante GitHub Pages.
- Validación del `.ics` antes de publicar.

## Estado inicial (18/09/2026)

El feed está precargado con los 22 partidos del Apertura 2026 y resultados de las jornadas disputadas. La Jornada 10 Antigua GFC–Municipal está fijada al **8 de octubre de 2026, 19:00**, conforme al comunicado de reprogramación de Liga Nacional.

## Instalación local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/seed.py
python scripts/generate_ics.py
python scripts/validate.py
```

## Publicación

1. Crea un repositorio público o privado en GitHub y sube todo el contenido de esta carpeta.
2. En GitHub: **Settings → Pages → Source: GitHub Actions**.
3. Ejecuta manualmente **Actions → Municipal Calendar — sync & publish → Run workflow**.
4. GitHub Pages publicará `municipal.ics` en la URL del repositorio.
5. En Google Calendar, Apple Calendar u Outlook agrega esa URL como calendario por suscripción.

## Cómo se actualiza una reprogramación

El partido conserva su UID. Si cambia fecha, hora, estado o resultado, el sincronizador registra el cambio en `match_history`, incrementa `SEQUENCE` y vuelve a generar el feed. El calendario del usuario recibirá el mismo evento actualizado cuando su proveedor refresque la suscripción.

## Importante

Google Calendar, Apple Calendar y Outlook controlan su propia frecuencia de refresco de calendarios suscritos; el sistema puede publicar una modificación inmediatamente, pero el cliente no necesariamente la mostrará al instante.

## Fuentes y prioridad

- Liga Nacional: calendario y comunicados oficiales.
- ESPN: puede incorporarse como fuente secundaria en una futura iteración para resultados/detección, pero nunca debe desplazar una reprogramación oficial.
