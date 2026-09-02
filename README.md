# jarvis
Asistente virtual por voz para Windows.

## Instalación

Requiere Python 3.10+ y PyAudio (en Windows suele instalarse con `pip install PyAudio`).

```bash
pip install -r requirements.txt
```

## Configuración

1. Copia `config.ejemplo.json` y renómbralo a `config.json`:

   ```bash
   cp config.ejemplo.json config.json
   ```

2. Edita `config.json` con tus datos:

   | Campo | Qué pones |
   |---|---|
   | `email.usuario` | Tu correo Gmail real |
   | `email.app_password` | App Password de Gmail (ajustes → verificación en 2 pasos → contraseñas de aplicaciones) |
   | `gemini.api_key` | Tu API key de Google Gemini (https://aistudio.google.com) |
   | `nombre_usuario` | Tu nombre (ej. "Ramiro") |
   | `saludo` | Personaliza el saludo. Usa `{saludo_hora}`, `{usuario}` y `{asistente}`. |
   | `respuesta_jarvis` | Qué dice Jarvis al oír la palabra "jarvis" |
   | `sin_tareas` | Mensaje cuando no hay tareas programadas |
   | `tiempo_inactividad_seg` | Segundos de inactividad antes de volver a dormir |
   | `rutina` | Horarios de cada día (`"hora": "HH:MM"`, `"tarea": "..."`) |
   | `musica.canciones` | Abreviaciones de voz → URL o búsqueda de YouTube |

> **⚠️ IMPORTANTE**: `config.json` está en `.gitignore` porque contiene credenciales reales. **No lo subas a GitHub.** Usa `config.ejemplo.json` como referencia de la estructura si compartes el proyecto.

## Uso

```bash
python jarvis.py
```

### Comandos de voz

| Comando                                   | Acción                              |
|-------------------------------------------|-------------------------------------|
| "jarvis"                                  | Preparar asistente                  |
| "abre el navegador"                       | Abre el navegador                   |
| "¿qué tengo que hacer hoy?"               | Lista la rutina del día             |
| "¿cuál es la próxima tarea?"              | Dice la próxima tarea               |
| "¿tengo correos nuevos?"                  | Cuenta no leídos en Gmail           |
| "reproduce black in black"                | Reprocha la canción en YouTube (auto-play) |
| "pregúntale a jarvis [algo]"              | Pregunta a Gemini AI                |
| "salir" / "detente"                       | Cierra el asistente                 |

### Avisos automáticos

El asistente corre en segundo plano un hilo que anuncia por voz cada tarea de la rutina un minuto antes de su hora, y consulta correos en segundo plano según `intervalo_minutos`.

### Modo dormido / despierto

El asistente arranca en **modo dormido**: escucha el micrófono en silencio e ignora todo salvo la palabra **"jarvis"**. Al escucharla se despierta, saluda y queda atento a tus órdenes. Tras `tiempo_inactividad_seg` (60 s por defecto) sin comandos, vuelve a dormirse.

### Saludo según la hora

Al despertar, Jarvis saluda dependiendo de la hora actual:

| Hora | Saludo |
|---|---|
| 5:00 – 11:59 | Buenos días señor {nombre}, ¿en qué trabajamos hoy? |
| 12:00 – 19:59 | Buenas tardes señor {nombre}, ¿en qué trabajamos hoy? |
| 20:00 – 4:59 | Buenas noches señor {nombre}, ¿en qué trabajamos hoy? |