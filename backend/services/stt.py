"""STT : voix -> texte (Whisper).

Si Whisper n'est pas installé ou désactivé, cette fonction n'est pas utilisée :
on passe directement par le champ texte de l'API (voir main.py).
"""
from __future__ import annotations

import tempfile
from pathlib import Path

from config import WHISPER_ACTIVE, WHISPER_MODEL

_model = None  # chargé une seule fois au premier appel


def _charger_model():
    """Chargement paresseux : le modèle ne se télécharge qu'une fois."""
    global _model
    if _model is None:
        from faster_whisper import WhisperModel  # import tardif
        _model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
    return _model


def dispo() -> bool:
    if not WHISPER_ACTIVE:
        return False
    try:
        import faster_whisper  # noqa
        return True
    except ImportError:
        return False


def transcrire(contenu: bytes) -> str:
    """Contenu audio (webm/wav/mp4…) -> texte."""
    model = _charger_model()
    with tempfile.NamedTemporaryFile(suffix=".audio", delete=False) as tmp:
        tmp.write(contenu)
        chemin = tmp.name
    try:
        segments, _ = model.transcribe(
            chemin,
            language="wo",   # wolof — Whisper tentera aussi le français si besoin
            beam_size=5,
        )
        return " ".join(s.text.strip() for s in segments).strip()
    finally:
        Path(chemin).unlink(missing_ok=True)
