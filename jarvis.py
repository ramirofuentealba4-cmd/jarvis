import json
import os
import threading
import webbrowser
import speech_recognition as sr

import correo
import musica
import rutina
from voz import hablar, escuchar, calibrar

RUTA_CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

BANNER = """
=====================================
  JARVIS - Asistente de Voz
=====================================
Comandos disponibles:
  "revisa el correo"        -> Cuenta correos nuevos
  "abre el navegador"       -> Abre el navegador
  "qué tengo que hacer hoy" -> Lista la rutina
  "cuál es la próxima"      -> Próxima tarea
  "reproduce [cancion]"     -> Abre en YouTube
  "salir" / "detente"       -> Cierra Jarvis
=====================================
"""


def cargar_config():
    with open(RUTA_CONFIG, "r", encoding="utf-8") as f:
        return json.load(f)


def procesar(comando, config):
    print(f"\nProcesando comando: '{comando}'", flush=True)

    if "salir" in comando or "detente" in comando or "apágate" in comando:
        print("Comando: salir", flush=True)
        hablar("Hasta luego.")
        return False

    if "abre el navegador" in comando or ("abre" in comando and "navegador" in comando):
        print("Comando: abrir navegador", flush=True)
        webbrowser.open("https://www.google.com")
        hablar("Abriendo el navegador.")
        return True

    if "correo" in comando or "correo" in comando:
        print("Comando: revisar correos", flush=True)
        hablar(correo.texto_no_leidos(config))
        return True

    if "hacer hoy" in comando or "tareas de hoy" in comando:
        print("Comando: tareas de hoy", flush=True)
        tareas = rutina.tareas_hoy(config)
        if tareas:
            lista = " ".join(f"a las {t['hora']}, {t['tarea']}." for t in tareas)
            hablar(f"Hoy tienes: {lista}")
        else:
            hablar("Hoy no tienes tareas programadas.")
        return True

    if "próxima" in comando or "proxima" in comando:
        print("Comando: próxima tarea", flush=True)
        hablar(rutina.proximo_aviso_texto(config))
        return True

    if musica.es_cancion(config, comando):
        print("Comando: reproducir música", flush=True)
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
        print("Comando: saludo por nombre", flush=True)
        hablar("Dime, ¿qué necesitas?")
        return True

    print("Comando no reconocido.", flush=True)
    hablar("No entendí eso. Puedes decir: correo, navegador, tareas, o reproduce música.")
    return True


def main():
    print(BANNER, flush=True)
    config = cargar_config()

    recognizer = sr.Recognizer()
    indice = config.get("microfono_indice")
    if indice is not None:
        mic = sr.Microphone(device_index=indice)
        print(f"Usando micrófono índice: {indice}", flush=True)
    else:
        mic = sr.Microphone()
        print("Usando micrófono por defecto.", flush=True)

    calibrar(recognizer, mic)
    hablar(f"Hola, soy {config['nombre_asistente']}. ¿En qué te ayudo?")

    rutina.iniciar(config, hablar)
    correo.iniciar_avisos(config, hablar)
    tareas = rutina.tareas_hoy(config)
    if tareas:
        hablar(rutina.proximo_aviso_texto(config))

    timeout_escucha = config.get("timeout_escucha", 7)
    duracion_frase = config.get("duracion_frase", 8)

    activo = True
    while activo:
        comando = escuchar(recognizer, mic, config["idioma"], timeout_escucha, duracion_frase)
        if comando:
            activo = procesar(comando, config)


if __name__ == "__main__":
    main()