import imaplib
import threading
import time

_ultimo_aviso = 0

def _avisador(config, hablar):
    global _ultimo_aviso
    while True:
        intervalo = config["email"]["intervalo_minutos"] * 60
        time.sleep(intervalo)
        n = correos_no_leidos(config)
        if n is not None and n > _ultimo_aviso:
            hablar(f"Llegaron {n} correos nuevos.")
        _ultimo_aviso = n if n is not None else _ultimo_aviso

def iniciar_avisos(config, hablar):
    t = threading.Thread(target=_avisador, args=(config, hablar), daemon=True)
    t.start()

def _conectar(config):
    mail = imaplib.IMAP4_SSL(config["email"]["imap_host"])
    mail.login(config["email"]["usuario"], config["email"]["app_password"])
    return mail

def correos_no_leidos(config):
    try:
        mail = _conectar(config)
        mail.select("inbox")
        _, datos = mail.search(None, "UNSEEN")
        n = len(datos[0].split()) if datos and datos[0] else 0
        mail.logout()
        return n
    except Exception:
        return None

def texto_no_leidos(config):
    n = correos_no_leidos(config)
    if n is None:
        return "No pude revisar los correos."
    if n == 0:
        return "No tienes correos nuevos."
    if n == 1:
        return "Tienes 1 correo nuevo."
    return f"Tienes {n} correos nuevos."