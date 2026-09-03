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
   | `gemini.api_key` | API key de Google Gemini (https://aistudio.google.com) |
   | `groq.api_key` | API key gratuita de Groq (https://console.groq.com) |
   | `cerebras.api_key` | API key gratuita de Cerebras (https://cloud.cerebras.ai) |
   | `auto_musica_url` | URL de YouTube que Jarvis abre al arrancar |
   | `nombre_usuario` | Tu nombre (ej. "Ramiro") |
   | `saludo` | Personaliza el saludo. Usa `{saludo_hora}`, `{usuario}` y `{asistente}`. |
   | `respuesta_jarvis` | Qué dice Jarvis al oír la palabra "jarvis" |
   | `sin_tareas` | Mensaje cuando no hay tareas programadas |
   | `tiempo_inactividad_seg` | Segundos de inactividad antes de avisar |
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
| (sin comando previo)                      | Jarvis arranca y escucha directamente |
| "abre el navegador"                       | Abre el navegador                   |
| "¿qué tengo que hacer hoy?"               | Lista la rutina del día             |
| "¿cuál es la próxima tarea?"              | Dice la próxima tarea               |
| "¿tengo correos nuevos?"                  | Cuenta no leídos en Gmail           |
| "reproduce black in black"                | Reproduce la canción en YouTube (auto-play) |
| "pregúntale a jarvis [algo]"              | Pregunta a la IA (Gemini/Groq/Cerebras) |
| "salir" / "detente"                       | Cierra el asistente                 |

### Avisos automáticos

El asistente corre en segundo plano un hilo que anuncia por voz cada tarea de la rutina un minuto antes de su hora, y consulta correos en segundo plano según `intervalo_minutos`.

### Arranque inmediato y auto-música

Jarvis arranca en **escucha activa**: al ejecutar `python jarvis.py` calibra el micrófono, saluda, **abre automáticamente** la URL de `auto_musica_url` (por defecto una playlist de YouTube) y queda escuchando tus órdenes sin necesidad de palabra de activación. Tras `tiempo_inactividad_seg` (60 s por defecto) te avisa en voz, pero sigue escuchando.

> Para desactivar la auto-música, pon `"auto_musica_url": null` en tu `config.json`.

### Motor multi-IA (Gemini, Groq y Cerebras)

Cuando pides algo que Jarvis no reconoce, consulta a la **IA** con **fallback automático** entre tres proveedores gratuitos, en este orden:

1. **Gemini** (Google) — `gemini-3.8-flash`
2. **Groq** — `llama-3.3-70b-versatile`
3. **Cerebras** — `gpt-oss-120b`

Si uno falla (quota, red, error), pasa al siguiente. Si quieres usar solo uno, deja los otros sin configurar.

#### Obtener las API keys (gratis, sin tarjeta)

| Servicio | Dónde conseguir la key |
|---|---|
| **Gemini** | https://aistudio.google.com/apikey → "Create API key" (ej. `AIza...`) |
| **Groq** | https://console.groq.com → crea cuenta → "API Keys" → "Create API Key" (ej. `gsk_...`) |
| **Cerebras** | https://cloud.cerebras.ai → crea cuenta → "API Keys" (ej. `cerebras_...`) |

Pega cada key en la sección correspondiente de `config.json` (`gemini.api_key`, `groq.api_key`, `cerebras.api_key`).

### Saludo según la hora

Al arrancar, Jarvis saluda dependiendo de la hora actual:

| Hora | Saludo |
|---|---|
| 5:00 – 11:59 | Buenos días señor {nombre}, ¿en qué trabajamos hoy? |
| 12:00 – 19:59 | Buenas tardes señor {nombre}, ¿en qué trabajamos hoy? |
| 20:00 – 4:59 | Buenas noches señor {nombre}, ¿en qué trabajamos hoy? |

## Servidor MCP (Model Context Protocol)

Jarvis también puede exponerse como **servidor MCP**, lo que permite que cualquier IA compatible (Claude Desktop, ChatGPT, VS Code, opencode, etc., incluidas las gratuitas) use las capacidades de Jarvis como herramientas.

### Herramientas expuestas

| Herramienta | Descripción |
|---|---|
| `hablar_jarvis(texto)` | Jarvis dice el texto en voz alta (voz chilena `es-CL-LorenzoNeural`) |
| `preguntar_ia(pregunta)` | Consulta a la IA (Gemini, Groq o Cerebras con fallback) |
| `leer_correos()` | Cuenta correos no leídos de Gmail |
| `tareas_hoy()` | Lista las tareas de la rutina de hoy |
| `proxima_tarea()` | Siguiente tarea programada |
| `reproducir_musica(cancion)` | Reproduce una canción en YouTube |

### Requisitos

```bash
pip install "mcp[cli]"
```

El servidor lee `config.json`, así que asegúrate de tenerlo configurado (ver sección **Configuración**).

### Probar localmente

```bash
python mcp_server.py
```

### Conectar desde Claude Desktop

Edita tu `claude_desktop_config.json` y añade:

```json
{
  "mcpServers": {
    "jarvis": {
      "command": "python",
      "args": ["C:\\ruta\\completa\\a\\jarvis\\mcp_server.py"]
    }
  }
}
```

### Conectar desde opencode

En tu `opencode.json`:

```json
{
  "mcp": {
    "jarvis": {
      "type": "local",
      "command": ["python", "mcp_server.py"],
      "enabled": true
    }
  }
}
```

(ajusta `command` con la ruta completa de `mcp_server.py` si es necesario)
