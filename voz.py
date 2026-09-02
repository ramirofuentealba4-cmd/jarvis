import threading
import pyttsx3
from speech_recognition import UnknownValueError, RequestError

_engine = None
_engine_lock = threading.Lock()

def hablar(texto):
    global _engine
    with _engine_lock:
        if _engine is None:
            _engine = pyttsx3.init()
        _engine.say(texto)
        _engine.runAndWait()

def calibrar(recognizer, fuente):
    print("Calibrando micrófono...", flush=True)
    with fuente:
        recognizer.adjust_for_ambient_noise(fuente, duration=1.0)
    print(f"Umbral de energía: {recognizer.energy_threshold}", flush=True)
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
        return ""
    except RequestError as e:
        print(f"Error de reconocimiento: no hay conexión con el servicio de voz. ({e})", flush=True)
        return ""
    except Exception as e:
        print(f"Error de reconocimiento: {e}", flush=True)
        return ""