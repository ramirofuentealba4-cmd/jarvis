import asyncio
import json
import os

from mcp.server.mcpserver import MCPServer

import correo
import gemini
import musica
import rutina
from voz import hablar

RUTA_CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

mcp = MCPServer("Jarvis")

_config = None


def _cargar_config():
    global _config
    if _config is None:
        if not os.path.exists(RUTA_CONFIG):
            raise FileNotFoundError(
                "No se encontró config.json. Copia config.ejemplo.json a config.json y completa tus datos."
            )
        with open(RUTA_CONFIG, "r", encoding="utf-8") as f:
            _config = json.load(f)
    return _config


@mcp.tool()
def hablar_jarvis(texto: str) -> str:
    """Hace que Jarvis diga en voz alta el texto dado (voz chilena es-CL-LorenzoNeural)."""
    hablar(texto)
    return f"Jarvis dijo: {texto}"


@mcp.tool()
def preguntar_gemini(pregunta: str) -> str:
    """Hace una pregunta a Gemini AI y devuelve la respuesta en texto."""
    config = _cargar_config()
    return gemini.preguntar_gemini(config, pregunta)


@mcp.tool()
def leer_correos() -> str:
    """Cuenta los correos no leídos de la bandeja de entrada de Gmail."""
    config = _cargar_config()
    return correo.texto_no_leidos(config)


@mcp.tool()
def tareas_hoy() -> str:
    """Lista las tareas de la rutina programadas para hoy."""
    config = _cargar_config()
    tareas = rutina.tareas_hoy(config)
    if not tareas:
        return config.get("sin_tareas", "Hoy no hay tareas programadas.")
    return "\n".join(f"- {t['hora']}: {t['tarea']}" for t in tareas)


@mcp.tool()
def proxima_tarea() -> str:
    """Devuelve la siguiente tarea programada de la rutina de hoy."""
    config = _cargar_config()
    return rutina.proximo_aviso_texto(config)


@mcp.tool()
def reproducir_musica(cancion: str) -> str:
    """Reproduce una canción en YouTube (usa el catálogo del config si existe la clave)."""
    config = _cargar_config()
    return musica.reproducir(config, cancion)


async def main():
    await mcp.run_stdio_async()


if __name__ == "__main__":
    asyncio.run(main())
