"""Réglages du projet — tout ce qui se modifie souvent est ici."""

# ---------------------------------------------------------------- Langue
# Une seule convention d'orthographe pour tout le projet :
# alphabet latin avec ñ et ŋ (à valider avec des locuteurs natifs)
LANGUE = "wo"

# ---------------------------------------------------------------- STT (Whisper)
# "tiny" = rapide et léger | "small" = plus précis
WHISPER_MODEL = "small"
# Si False, l'API accepte du texte direct (utile pour tester sans micro)
WHISPER_ACTIVE = True

# ---------------------------------------------------------------- TTS (Piper)
# Chemin vers la voix téléchargée (voir README, étape 2)
PIPER_VOICE = "models/fr_FR-siwis-medium.onnx"
TTS_ACTIVE = False   # passer à True une fois le modèle téléchargé

# ---------------------------------------------------------------- LLM (Ollama)
LLM_ACTIVE = False            # passer à True si Ollama est installé
LLM_MODEL = "llama3.2"        # ollama pull llama3.2

# ---------------------------------------------------------------- Villes reconnues
# (latitude, longitude) — servies par Open-Meteo gratuitement
VILLES = {
    "dakar": (14.7, -17.5),
    "thies": (14.8, -16.9),
    "touba": (14.85, -15.9),
    "kaolack": (14.15, -16.07),
    "saint-louis": (16.03, -16.5),
    "ziguinchor": (12.58, -16.27),
    "mbour": (14.42, -16.96),
    "diourbel": (14.65, -16.23),
    "sokhna": None,   # "sokhna" = marché en wolof, pas une ville
}
