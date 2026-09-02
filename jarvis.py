import json
import os
import threading
import webbrowser
import speech_recognition as sr

import correo
import musica
import rutina
from voz import hablar, escuchar

RUTA_CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def cargar_config():
    with open(RUTA_CONFIG, "r", encoding="utf-8") as f:
        return json.load(f)


def procesar(comando, config):
    if "salir" in comando or "detente" in comando or "apágate" in comando:
        hablar("Hasta luego.")
        return False

    if "abre el navegador" in comando or ("abre" in comando and "navegador" in comando):
        webbrowser.open("https://www.google.com")
        hablar("Abriendo el navegador.")
        return True

    if "correo" in comando:
        hablar(correo.texto_no_leidos(config))
        return True

    if "hacer hoy" in comando or "tareas de hoy" in comando:
        tareas = rutina.tareas_hoy(config)
        if tareas:
            lista = " ".join(f"a las {t['hora']}, {t['tarea']}." for t in tareas)
            hablar(f"Hoy tienes: {lista}")
        else:
            hablar("Hoy no tienes tareas programadas.")
        return True

    if "próxima" in comando or "proxima" in comando:
        hablar(rutina.proximo_aviso_texto(config))
        return True

    if musica.es_cancion(config, comando):
        cancion = ""
        for prefijo in ("reproduce ", "ponme la canción ", "ponme la cancion ", "pon ", "toca "):
            if prefijo in comando:
                cancion = comando.split(prefijo, 1)[1].strip()
                break
        if not cancion:
            cancion = "back in black ac dc"
        hablar(musica.reproducir(config, cancion))
        return True

    if comando.startswith(tuple(config["clave_asistente"])):
        hablar("Dime, ¿qué necesitas?")
        return True

    return True


def main():
    config = cargar_config()
    hablar(f"Hola, soy {config['nombre_asistente']}. ¿En qué te ayudo?")
    rutina.iniciar(config, hablar)
    correo.iniciar_avisos(config, hablar)
    tareas = rutina.tareas_hoy(config)
    if tareas:
        hablar(rutina.proximo_aviso_texto(config))

    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    activo = True
    while activo:
        comando = escuchar(recognizer, mic, config["idioma"])
        if comando:
            activo = procesar(comando, config)


if __name__ == "__main__":
    main()