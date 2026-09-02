from google import genai

_cliente = None

def _inicializar(config):
    global _cliente
    if _cliente is None:
        api_key = config["gemini"]["api_key"]
        _cliente = genai.Client(api_key=api_key)

def preguntar_gemini(config, texto):
    try:
        _inicializar(config)
        modelo = config["gemini"].get("modelo", "gemini-2.0-flash")
        system = config["gemini"].get("system_prompt", "Eres Jarvis, un asistente de voz. Responde en español, breve y natural.")
        respuesta = _cliente.models.generate_content(
            model=modelo,
            contents=f"{system}\n\nUsuario: {texto}"
        )
        return respuesta.text
    except Exception as e:
        print(f"Error de Gemini: {type(e).__name__}: {e}", flush=True)
        return "No pude conectarme con Gemini en este momento."