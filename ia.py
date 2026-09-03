import os

import gemini

PROVIDERES = ("gemini", "groq", "cerebras")

SYSTEM_DEFAULT = (
    "Eres Jarvis, un asistente de voz amigable. "
    "Responde en español, de forma breve y natural (máximo 2 oraciones). "
    "Sé útil pero conciso."
)


def _key_valida(key):
    return bool(key) and not key.startswith("TU_") and "TU_API_KEY" not in key


def _es_fallo(texto):
    if not texto:
        return True
    fallos = (
        "no pude conectarme", "no pude revisar", "es inválida", "no está configurada",
        "no existe", "límite", "no hay conexión", "no pude conectar",
        "hubo un error", "no tengo conexión",
    )
    bajo = texto.lower()
    return any(f in bajo for f in fallos)


def _config_valido(config, proveedor):
    datos = config.get(proveedor, {})
    if proveedor == "gemini":
        return _key_valida(datos.get("api_key", ""))
    return _key_valida(datos.get("api_key", "")) and bool(datos.get("base_url", ""))


def _preguntar_groq_cerebras(config, proveedor, texto):
    import openai

    datos = config.get(proveedor, {})
    client = openai.OpenAI(
        base_url=datos["base_url"],
        api_key=datos["api_key"],
    )
    modelo = datos.get("modelo", "")
    system = datos.get("system_prompt", SYSTEM_DEFAULT)
    respuesta = client.chat.completions.create(
        model=modelo,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": texto},
        ],
    )
    contenido = respuesta.choices[0].message.content
    if not contenido:
        raise RuntimeError(f"{proveedor} devolvió una respuesta vacía")
    return contenido


def _traducir_error_final(errores):
    mensajes = [f"- {p}: {tipo}: {mensaje}" for p, tipo, mensaje in errores if mensaje]
    return (
        "No pude conectarme con ninguna IA en este momento. "
        f"Errores:\n" + "\n".join(mensajes)
    )


def preguntar_ia(config, texto):
    errores = []

    if _config_valido(config, "gemini"):
        try:
            resultado = gemini.preguntar_gemini(config, texto)
        except Exception as e:
            errores.append(("gemini", type(e).__name__, str(e)))
            print(f"Gemini falló, probando otro proveedor: {e}", flush=True)
        else:
            if _es_fallo(resultado):
                errores.append(("gemini", "Respuesta de error", resultado))
                print(f"Gemini falló, probando otro proveedor: {resultado}", flush=True)
            else:
                return resultado
    else:
        errores.append(("gemini", "Sin configurar", None))

    for proveedor in ("groq", "cerebras"):
        if not _config_valido(config, proveedor):
            errores.append((proveedor, "Sin configurar", None))
            continue
        try:
            return _preguntar_groq_cerebras(config, proveedor, texto)
        except Exception as e:
            errores.append((proveedor, type(e).__name__, str(e)))
            print(f"{proveedor} falló: {e}", flush=True)

    return _traducir_error_final(errores)
