import json
import os
import threading
import time
import webbrowser
from datetime import datetime
import speech_recognition as sr

import correo
import gemini
import musica
import rutina
from voz import hablar, escuchar, calibrar

RUTA_CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

BANNER = """
=====================================
  JARVIS - Asistente de Voz
=====================================
Comandos disponibles:
  "revisa el correo"             -> Cuenta correos nuevos
  "abre el navegador"            -> Abre el navegador
  "qué tengo que hacer hoy"      -> Lista la rutina
  "cuál es la próxima"           -> Próxima tarea
  "reproduce [cancion]"          -> Abre en YouTube
  "pregúntale a jarvis [algo]"   -> Pregunta a Gemini AI
  "salir" / "detente"            -> Cierra Jarvis
=====================================
"""


def cargar_config():
    if not os.path.exists(RUTA_CONFIG):
        print("=" * 50, flush=True)
        print("Error: no se encontró config.json", flush=True)
        print("Para crearlo, ejecuta:", flush=True)
        print("  cp config.ejemplo.json config.json", flush=True)
        print("  y completa tus datos (Gmail, API key, nombre, rutina).", flush=True)
        print("=" * 50, flush=True)
        hablar("No encontré config.json. Crea tu archivo de configuración con cp config.ejemplo.json config.json")
        return None
    with open(RUTA_CONFIG, "r", encoding="utf-8") as f:
        return json.load(f)


def saludo_por_hora():
    hora = datetime.now().hour
    if 5 <= hora < 12:
        return "Buenos días"
    elif 12 <= hora < 20:
        return "Buenas tardes"
    else:
        return "Buenas noches"


def generar_saludo(config):
    saludo_hora = saludo_por_hora()
    plantilla = config.get("saludo", "=== {saludo_hora} señor {usuario}, ¿en qué trabajamos hoy?")
    return (plantilla
            .replace("{saludo_hora}", saludo_hora)
            .replace("{usuario}", config.get("nombre_usuario", ""))
            .replace("{asistente}", config["nombre_asistente"]))


def respuesta_jarvis(config):
    return config.get("respuesta_jarvis", "Hola soy Jarvis, ¿cómo te ayudo?")


def procesar(comando, config):
    print(f"\nProcesando comando: '{comando}'", flush=True)

    try:
        if "salir" in comando or "detente" in comando or "apágate" in comando:
            print("Comando: salir", flush=True)
            hablar("Hasta luego.")
            return False

        if "abre el navegador" in comando or ("abre" in comando and "navegador" in comando):
            print("Comando: abrir navegador", flush=True)
            webbrowser.open("https://www.google.com")
            hablar("Abriendo el navegador.")
            return True

        if "correo" in comando:
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
                hablar(config.get("sin_tareas", "Hoy no quedan más tareas programadas."))
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

        for prefijo in ("pregúntale a jarvis ", "pregunta a jarvis ", "pregúntale a jarvis", "pregunta a jarvis"):
            if prefijo in comando:
                pregunta = comando.split(prefijo, 1)[1].strip() if prefijo in comando else ""
                if pregunta:
                    print(f"Gemini: '{pregunta}'", flush=True)
                    hablar(gemini.preguntar_gemini(config, pregunta))
                else:
                    hablar("¿Qué quieres preguntarle a Jarvis?")
                return True

        print("No reconocido, consultando a Gemini...", flush=True)
        hablar("Un momento, estoy consultando con Gemini.")
        respuesta = gemini.preguntar_gemini(config, comando)
        hablar(respuesta)
        return True

    except Exception as e:
        print(f"Error al ejecutar comando: {type(e).__name__}: {e}", flush=True)
        hablar(f"Hubo un error: {e}")
        return True


def contiene_clave(comando, config):
    return comando.startswith(tuple(config["clave_asistente"]))


def iniciar_sesion_activa(config, recognizer, mic, timeout_escucha, duracion_frase, inactividad_seg):
    hablar(respuesta_jarvis(config))
    ultima_actividad = time.time()
    while True:
        if time.time() - ultima_actividad > inactividad_seg:
            hablar(config.get("saludo_inactividad", "Dime jarvis si me necesitas."))
            return True

        comando = escuchar(recognizer, mic, config["idioma"], timeout_escucha, duracion_frase)
        if not comando:
            continue
        ultima_actividad = time.time()
        activo = procesar(comando, config)
        if not activo:
            return False


def main():
    print(BANNER, flush=True)
    config = cargar_config()
    if config is None:
        return

    recognizer = sr.Recognizer()
    indice = config.get("microfono_indice")
    if indice is not None:
        mic = sr.Microphone(device_index=indice)
        print(f"Usando micrófono índice: {indice}", flush=True)
    else:
        mic = sr.Microphone()
        print("Usando micrófono por defecto.", flush=True)

    calibrar(recognizer, mic)
    hablar(generar_saludo(config))

    rutina.iniciar(config, hablar)
    correo.iniciar_avisos(config, hablar)

    timeout_escucha = config.get("timeout_escucha", 7)
    duracion_frase = config.get("duracion_frase", 8)
    inactividad_seg = config.get("tiempo_inactividad_seg", 60)

    hablar("Estoy en modo dormido. Di jarvis para despertarme.")
    while True:
        comando = escuchar(recognizer, mic, config["idioma"], timeout_escucha, 4)
        if not comando:
            continue
        if contiene_clave(comando, config):
            seguir = iniciar_sesion_activa(config, recognizer, mic, timeout_escucha, duracion_frase, inactividad_seg)
            if seguir is False:
                break
            hablar("Vuelvo a dormir. Di jarvis si me necesitas.")


if __name__ == "__main__":
    main()