import asyncio
import os
import platform
import tempfile
import threading

import edge_tts
import speech_recognition as sr
from speech_recognition import UnknownValueError, RequestError

VOZ_POR_DEFECTO = "es-CL-LorenzoNeural"
_audio_lock = threading.Lock()


def _reproducir_mp3(ruta):
    try:
        import pygame
        pygame.mixer.init()
        pygame.mixer.music.load(ruta)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.wait(50)
        pygame.mixer.quit()
        return
    except ImportError:
        pass
    except Exception as e:
        print(f"Error pygame: {e}", flush=True)

    if platform.system() == "Windows":
        os.system(f'start /wait "" "{ruta}"')
    elif platform.system() == "Darwin":
        os.system(f'afplay "{ruta}"')
    else:
        os.system(f'mpv --no-video "{ruta}" 2>/dev/null || ffplay -nodisp -autoexit "{ruta}" 2>/dev/null')


async def _generar_audio(texto, ruta, voz):
    communicate = edge_tts.Communicate(texto, voz)
    await communicate.save(ruta)


def hablar(texto, voz=None):
    print(f"JARVIS: {texto}", flush=True)

    if not texto or not texto.strip():
        return

    voz = voz or VOZ_POR_DEFECTO

    with _audio_lock:
        tmp = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                tmp = f.name

            asyncio.run(_generar_audio(texto, tmp, voz))
            _reproducir_mp3(tmp)
        except Exception as e:
            print(f"Error al hablar: {e}", flush=True)
        finally:
            if tmp and os.path.exists(tmp):
                try:
                    os.unlink(tmp)
                except Exception:
                    pass


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