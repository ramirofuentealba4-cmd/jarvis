import sys
import threading
from speech_recognition import UnknownValueError, RequestError

_engine = None
_engine_lock = threading.Lock()
_voz_disponible = False

try:
    import pyttsx3
    _voz_disponible = True
except Exception as e:
    print(f"pyttsx3 no disponible: {e}", flush=True)
    _voz_disponible = False


def _crear_engine():
    try:
        engine = pyttsx3.init()
        voces = engine.getProperty("voices")
        for v in voces:
            if "spanish" in v.id.lower() or "es_" in v.id.lower() or "es-" in v.id.lower():
                engine.setProperty("voice", v.id)
                break
        return engine
    except Exception as e:
        print(f"No se pudo inicializar el motor de voz: {e}", flush=True)
        return None


def hablar(texto):
    global _engine
    print(f"JARVIS: {texto}", flush=True)

    if not _voz_disponible:
        return

    with _engine_lock:
        try:
            if _engine is None:
                _engine = _crear_engine()
            if _engine is not None:
                _engine.say(texto)
                _engine.runAndWait()
        except Exception as e:
            print(f"Error al hablar: {e}", flush=True)


def calibrar(recognizer, fuente):
    hablar("Calibrando micrófono, dame un momento.")
    print("Calibrando micrófono...", flush=True)
    with fuente:
        recognizer.adjust_for_ambient_noise(fuente, duration=1.0)
    print(f"Umbral de energía: {recognizer.energy_threshold}", flush=True)
    hablar("Listo, ya puedo escucharte.")
    print("Micrófono calibrado.", flush=True)


def escuchar(recognizer, fuente, idioma="es-ES", timeout_escucha=7, duracion_frase=8):
    try:
        print("Escuchando...", flush=True)
        with fuente as source:
            audio = recognizer.listen(source, timeout=timeout_escucha, phrase_time_limit=duracion_frase)
        print("Procesando voz...", flush=True)
        texto = recognizer.recognize_google(audio, language=idioma)
        print(f"Reconocido: {texto}", flush=True)
        return texto.lower()
    except UnknownValueError:
        print("Error de reconocimiento: no pude entender lo que dijiste.", flush=True)
        hablar("No te escuché bien, repite por favor.")
        return ""
    except RequestError as e:
        print(f"Error de reconocimiento: no hay conexión con el servicio de voz. ({e})", flush=True)
        hablar("No tengo conexión con el servicio de voz.")
        return ""
    except Exception as e:
        print(f"Error de reconocimiento: {e}", flush=True)
        hablar("Hubo un error al escuchar.")
        return ""