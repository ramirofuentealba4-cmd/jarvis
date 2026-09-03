import platform
import threading
import speech_recognition as sr
from speech_recognition import UnknownValueError, RequestError

_engine = None
_engine_lock = threading.Lock()


def _crear_engine():
    global _engine
    try:
        if _engine is not None:
            try:
                _engine.stop()
            except Exception:
                pass
            _engine = None

        if platform.system() == "Windows":
            engine = pyttsx3.init(driverName="sapi5")
        else:
            engine = pyttsx3.init()

        voces = engine.getProperty("voices")
        for v in voces:
            if "spanish" in v.id.lower() or "es_" in v.id.lower() or "es-" in v.id.lower():
                engine.setProperty("voice", v.id)
                break

        rate = engine.getProperty("rate")
        engine.setProperty("rate", max(rate - 20, 100))
        _engine = engine
        return engine
    except Exception as e:
        print(f"No se pudo inicializar el motor de voz: {e}", flush=True)
        print("  Instala pyttsx3 con soporte TTS:", flush=True)
        print("  pip install pyttsx3 pypiwin32", flush=True)
        _engine = None
        return None


def _decir(texto):
    global _engine
    with _engine_lock:
        try:
            if _engine is None:
                _crear_engine()
            if _engine is None:
                return False

            _engine.say(texto)
            _engine.runAndWait()
            return True
        except Exception as e:
            print(f"Error al hablar: {e}", flush=True)
            try:
                _crear_engine()
                if _engine is not None:
                    _engine.say(texto)
                    _engine.runAndWait()
                    return True
            except Exception:
                pass
            return False


def hablar(texto):
    print(f"JARVIS: {texto}", flush=True)
    try:
        import pyttsx3
    except ImportError:
        print("pyttsx3 no instalado. Instala con: pip install pyttsx3", flush=True)
        return

    if not texto or not texto.strip():
        return

    if len(texto) > 300:
        partes = []
        for oracion in texto.replace("\n", " ").split(". "):
            oracion = oracion.strip()
            if oracion:
                partes.append(oracion)
        for parte in partes:
            if not parte.endswith((".", "!", "?")):
                parte += "."
            _decir(parte)
    else:
        _decir(texto)


def calibrar(recognizer, fuente):
    hablar("Calibrando micrófono, dame un momento.")
    with fuente:
        recognizer.adjust_for_ambient_noise(fuente, duration=1.0)
    hablar("Listo, ya puedo escucharte.")


def escuchar(recognizer, fuente, idioma="es-ES", timeout_escucha=7, duracion_frase=8):
    try:
        with fuente as source:
            audio = recognizer.listen(source, timeout=timeout_escucha, phrase_time_limit=duracion_frase)
        texto = recognizer.recognize_google(audio, language=idioma)
        print(f"Reconocido: {texto}", flush=True)
        return texto.lower()
    except UnknownValueError:
        hablar("No te escuché bien, repite por favor.")
        return ""
    except RequestError as e:
        print(f"Error de servicio de voz: {e}", flush=True)
        hablar("No tengo conexión con el servicio de voz.")
        return ""
    except Exception as e:
        print(f"Error de reconocimiento: {e}", flush=True)
        hablar("Hubo un error al escuchar.")
        return ""