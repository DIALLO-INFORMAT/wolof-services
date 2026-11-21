"""TTS : texte -> voix (Piper).

⚠️ Il n'existe pas encore de voix wolof officielle pour Piper.
On utilise donc une voix française : la voix lira le wolof écrit avec une
prononciation approximative. À long terme : enregistrer votre propre voix wolof.

Sans Piper installé, l'API renvoie seulement le texte (mode texte).
"""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

from config import PIPER_VOICE, TTS_ACTIVE


def dispo() -> bool:
    if not TTS_ACTIVE:
        return False
    return Path(PIPER_VOICE).exists()


def synthetiser(texte: str) -> str | None:
    """Retourne le chemin du fichier WAV généré, ou None si indisponible."""
    if not dispo():
        return None

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        sortie = tmp.name

    # Piper lit sur stdin, écrit le WAV sur stdout
    process = subprocess.run(
        ["piper", "--model", PIPER_VOICE, "--output_file", sortie],
        input=texte.encode("utf-8"),
        capture_output=True,
        check=False,
    )
    if process.returncode != 0:
        return None
    return sortie
