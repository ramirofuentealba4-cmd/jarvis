import threading
import time
from datetime import datetime, timedelta

DIAS = {
    "lunes": 0, "martes": 1, "miercoles": 2, "miércoles": 2,
    "jueves": 3, "viernes": 4, "sabado": 5, "sábado": 5, "domingo": 6
}

_avisos_emitidos = {}
_hilo = None

def _nombre_dia():
    return list(DIAS.keys())[datetime.now().weekday()]

def _avisar(config, hablar):
    while True:
        ahora = datetime.now()
        dia = _nombre_dia()
        tareas = config["rutina"].get(dia, [])
        for t in tareas:
            hh, mm = t["hora"].split(":")
            horario = ahora.replace(hour=int(hh), minute=int(mm), second=0, microsecond=0)
            previsto = horario - timedelta(minutes=1)
            clave = (dia, t["hora"])
            if previsto <= ahora <= horario and clave not in _avisos_emitidos:
                _avisos_emitidos[clave] = True
                hablar(f"Te recuerdo: {t['tarea']}")
        time.sleep(20)

def iniciar(config, hablar):
    global _hilo
    _hilo = threading.Thread(target=_avisar, args=(config, hablar), daemon=True)
    _hilo.start()

def tareas_hoy(config):
    dia = _nombre_dia()
    return config["rutina"].get(dia, [])

def proxima_tarea(config):
    dt = datetime.now()
    tareas = tareas_hoy(config)
    pendientes = [t for t in tareas if dt.strftime("%H:%M") < t["hora"]]
    if pendientes:
        pendientes.sort(key=lambda t: t["hora"])
        return pendientes[0]
    return None

def proximo_aviso_texto(config):
    prox = proxima_tarea(config)
    if prox:
        return f"La próxima tarea de hoy es a las {prox['hora']}: {prox['tarea']}"
    return "Hoy no quedan más tareas programadas."