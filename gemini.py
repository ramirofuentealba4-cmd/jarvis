from google import genai

_cliente = None

MARKER_API_KEY = "TU_API_KEY_DE_GEMINI"


def _inicializar(config):
    global _cliente
    if _cliente is None:
        api_key = config.get("gemini", {}).get("api_key", "")
        _cliente = genai.Client(api_key=api_key)


def _api_key_valida(config):
    key = config.get("gemini", {}).get("api_key", "")
    return bool(key) and key != MARKER_API_KEY and not key.startswith("TU_")


def _traducir_error(e):
    nombre = type(e).__name__
    mensaje = str(e).lower()
    if "not found" in mensaje or "404" in mensaje or "model" in mensaje and "not found" in mensaje:
        return "El modelo de Gemini configurado no existe. Actualiza 'modelo' en config.json."
    if "api key" in mensaje and ("invalid" in mensaje or "unauthorized" in mensaje or "401" in mensaje):
        return "Tu API key de Gemini es inválida. Revísala en config.json."
    if "quota" in mensaje or "quota exceeded" in mensaje or "429" in mensaje:
        return "Se alcanzó el límite gratuito de Gemini. Intenta más tarde."
    if "timeout" in mensaje or "timed out" in nombre or "connection" in mensaje and "failed" in mensaje:
        return "No hay conexión a internet o Gemini tardó demasiado."
    return "No pude conectarme con Gemini en este momento. Revisa la consola para más detalles."


def preguntar_gemini(config, texto):
    if not _api_key_valida(config):
        return ("Tu API key de Gemini no está configurada. "
                "Edita tu config.json y pon tu clave en gemini.api_key.")

    try:
        _inicializar(config)
        gem = config.get("gemini", {})
        modelo = gem.get("modelo", "gemini-3.8-flash")
        system = gem.get("system_prompt", "Eres Jarvis, un asistente de voz. Responde en español, breve y natural.")
        respuesta = _cliente.models.generate_content(
            model=modelo,
            contents=texto,
            config={
                "system_instruction": system,
            },
        )
        return respuesta.text
    except Exception as e:
        print(f"Error de Gemini: {type(e).__name__}: {e}", flush=True)
        return _traducir_error(e)