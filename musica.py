import webbrowser
from urllib.parse import quote

NO_MATCH = "No conozco esa canción. Repítela o mírala en YouTube."

def reproducir(config, nombre_cancion):
    canciones = config["musica"]["canciones"]
    clave = nombre_cancion.strip().lower()
    if clave in canciones:
        busqueda = canciones[clave]
    elif canciones:
        busqueda = clave
    else:
        busqueda = clave

    url = "https://www.youtube.com/results?search_query=" + quote(busqueda)
    webbrowser.open(url)
    return f"Reproduciendo {busqueda} en YouTube."

def es_cancion(config, comando):
    return any(b in comando for b in (" reproduce ", "pon", "ponme la canción", "toca ", "música"))