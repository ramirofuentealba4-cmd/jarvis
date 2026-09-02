import re
import webbrowser
from urllib.parse import quote

NO_MATCH = "No conozco esa canción. Repítela o mírala en YouTube."

def _extraer_video_id(url):
    patrones = [
        r'(?:v=|/v/|youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'embed/([a-zA-Z0-9_-]{11})',
    ]
    for p in patrones:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None

def reproducir(config, nombre_cancion):
    canciones = config["musica"]["canciones"]
    clave = nombre_cancion.strip().lower()
    busqueda = canciones.get(clave, clave)

    video_id = _extraer_video_id(busqueda)
    if video_id:
        url = f"https://www.youtube.com/embed/{video_id}?autoplay=1&mute=1"
    else:
        url = "https://www.youtube.com/results?search_query=" + quote(busqueda)

    webbrowser.open(url)
    return f"Reproduciendo {busqueda} en YouTube."

def es_cancion(config, comando):
    return any(b in comando for b in (" reproduce ", "pon", "ponme la canción", "toca ", "música"))