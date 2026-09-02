# jarvis
Asistente virtual por voz para Windows.

## Instalación

Requiere Python 3.10+ y PyAudio (en Windows suele instalarse con `pip install PyAudio`).

```bash
pip install -r requirements.txt
```

## Configuración

Edita `config.json`:

1. **Gmail**: genera una *App Password* en tu cuenta de Google (ajustes de seguridad → verificación en 2 pasos → contraseñas de aplicaciones) y ponla en `app_password`.
2. **Rutina**: completa los horarios de cada día en `rutina` usando el formato `"hora": "HH:MM"` y una `"tarea"` descriptiva.
3. **Música**: agrega en `canciones` los temas que quieras abreviar por voz (ej. `"black in black": "Back In Black AC/DC"`).

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
| "reproduce black in black"                | Abre la canción en YouTube          |
| "salir" / "detente"                       | Cierra el asistente                 |

### Avisos automáticos

El asistente corre en segundo plano un hilo que anuncia por voz cada tarea de la rutina un minuto antes de su hora, y consulta correos en segundo plano según `intervalo_minutos`.