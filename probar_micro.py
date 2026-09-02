import speech_recognition as sr

print("=" * 50)
print("  DIAGNÓSTICO DE MICRÓFONO - JARVIS")
print("=" * 50)

print("\n[1] Dispositivos de audio disponibles:")
print("-" * 40)
for i, name in enumerate(sr.Microphone.list_microphone_names()):
    print(f"  Índice {i}: {name}")

mic_default = sr.Microphone()
print(f"\nMicrófono por defecto: {mic_default}")

print("\n[2] Calibrando micrófono (3 segundos de silencio)...")
recognizer = sr.Recognizer()
with mic_default as source:
    recognizer.adjust_for_ambient_noise(source, duration=3.0)
print(f"  Umbral de energía: {recognizer.energy_threshold}")

print("\n[3] Grabando 4 segundos... HABLA AHORA")
try:
    with mic_default as source:
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
    print("  Audio grabado correctamente.")
except Exception as e:
    print(f"  Error al grabar: {type(e).__name__}: {e}")
    print("  El micrófono NO está captando audio.")
    print("\nIntenta con otro índice. Modifica config.json:")
    print('  "microfono_indice": 1   (o el índice que prefieras)')
    exit(1)

print("\n[4] Enviando a Google Speech Recognition...")
try:
    texto = recognizer.recognize_google(audio, language="es-ES")
    print(f"  Texto reconocido: '{texto}'")
    print("\n  ¡El micrófono y el reconocimiento funcionan!")
    print("  Si Jarvis no te entiende, el problema es de calibración.")
except Exception as e:
    print(f"  Error: {type(e).__name__}: {e}")
    print("\n  Posibles causas:")
    print("  - Sin conexión a internet")
    print("  - Google Speech no disponible")
    print("  - Audio muy bajo o ruido excesivo")
    exit(1)

print("\n" + "=" * 50)
print("  DIAGNÓSTICO COMPLETO")
print("=" * 50)