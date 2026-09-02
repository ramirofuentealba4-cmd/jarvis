import threading
import pyttsx3

_engine = None
_engine_lock = threading.Lock()

def hablar(texto):
    global _engine
    with _engine_lock:
        if _engine is None:
            _engine = pyttsx3.init()
        _engine.say(texto)
        _engine.runAndWait()

def escuchar(recognizer, fuente, idioma="es-ES"):
    try:
        with fuente:
            recognizer.adjust_for_ambient_noise(fuente, duration=0.4)
        print("Escuchando...")
        with fuente as source:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
        texto = recognizer.recognize_google(audio, language=idioma)
        print(f"Reconocido: {texto}")
        return texto.lower()
    except Exception as e:
        return ""