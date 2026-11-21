"""LLM optionnel (Ollama) — pour les questions libres en wolof.

Si Ollama n'est pas installé, on renvoie une réponse polie par défaut.
Installer : https://ollama.com puis :  ollama pull llama3.2
"""
from __future__ import annotations

import httpx

from config import LLM_ACTIVE, LLM_MODEL

OLLAMA_URL = "http://localhost:11434/api/generate"

SYSTEME = (
    "Tu es l'assistant « Wolof Services ». Tu réponds TOUJOURS en wolof "
    "écrit (alphabet latin, ñ et ŋ), de façon courte et simple. "
    "Si tu ne connais pas la réponse, dis-le poliment en wolof."
)


def dispo() -> bool:
    if not LLM_ACTIVE:
        return False
    try:
        httpx.get("http://localhost:11434", timeout=2)
        return True
    except Exception:
        return False


async def repondre(question: str) -> str:
    if not dispo():
        return (
            "Jërëm-jërëm, xam-xam bi weesu ci biir bi. "
            "Dañu ko yégal ci kanam."
        )  # « Désolé, l'information n'est pas encore disponible. »

    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(OLLAMA_URL, json={
            "model": LLM_MODEL,
            "prompt": f"{SYSTEME}\n\nQuestion : {question}\nRéponse :",
            "stream": False,
        })
        r.raise_for_status()
        return r.json().get("response", "").strip()
