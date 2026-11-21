"""Wolof Services — point d'entrée du backend.

Lancer :
    uvicorn main:app --reload
Puis ouvrir : http://127.0.0.1:8000/docs
"""
from __future__ import annotations

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from services import intent, llm, marche, meteo, sante, stt, tts

app = FastAPI(
    title="Wolof Services API",
    description="Services du quotidien en wolof — météo, marché, santé.",
    version="0.1.0",
)

# L'app Flutter tourne sur le téléphone → il faut autoriser les requêtes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # en production : remplacer par l'URL exacte de l'app
    allow_methods=["*"],
    allow_headers=["*"],
)


class DemandeTexte(BaseModel):
    """Pour tester sans micro : on envoie directement du texte."""
    texte: str


async def _repondre(intention: str, texte: str, ville: str | None) -> dict:
    """Route la demande vers le bon service et construit la réponse."""
    if intention == "meteo":
        return await meteo.previsions(ville)
    if intention == "marche":
        return marche.prix_produits(texte, ville)
    if intention == "sante":
        return await sante.pharmacies_proches()
    # Sinon : question libre → LLM (ou réponse polie par défaut)
    return {"texte": await llm.repondre(texte)}


@app.get("/")
def accueil():
    """Page d'accueil : petite carte de visite en wolof."""
    return {
        "platform": "Wolof Services 🇸🇳",
        "bienvenue": "Dalal ak jamm ! Bienvenue sur l'API des services du quotidien en wolof.",
        "essai": {"marche": "prix du riz Dakar",
                  "meteo": "meteo Dakar",
                  "sante": "pharmacie de garde Dakar"},
        "swagger": "/docs",
        "sante": "/health",
    }


@app.get("/health")
def health():
    """Vérifie ce qui est disponible sur ce serveur."""
    return {
        "status": "ok",
        "stt_whisper": stt.dispo(),
        "tts_piper": tts.dispo(),
        "llm_ollama": llm.dispo(),
    }


@app.post("/ask")
async def ask_texte(demande: DemandeTexte):
    """MODE TEXTE — le plus simple pour développer et tester.

    Exemple : {"texte": "meteo Dakar"}
    """
    intention, ville = intent.detecter(demande.texte)
    resultat = await _repondre(intention, demande.texte, ville)
    resultat.update({
        "intention": intention,
        "ville": ville,
        "audio": None,          # activé plus tard avec Piper
        "requete": demande.texte,
    })
    return resultat


@app.post("/ask/voix")
async def ask_voix(audio: UploadFile = File(...)):
    """MODE VOIX — l'audio du micro de l'app Flutter.

    Requiert Whisper (voir README étape 2). Sans Whisper, erreur claire.
    """
    if not stt.dispo():
        return JSONResponse(
            status_code=503,
            content={"erreur": "Whisper non installé — voir README étape 2. "
                               "Utilisez POST /ask en mode texte."},
        )

    contenu = await audio.read()
    texte = stt.transcrire(contenu)
    if not texte:
        return JSONResponse(
            status_code=422,
            content={"erreur": "Je n'ai rien compris, jërëm-jërëm."},
        )

    intention, ville = intent.detecter(texte)
    resultat = await _repondre(intention, texte, ville)

    # Synthèse vocale de la réponse (si Piper est actif)
    chemin_audio = tts.synthetiser(resultat.get("texte", ""))
    resultat.update({
        "intention": intention,
        "ville": ville,
        "requete": texte,
        "audio": "/audio" if chemin_audio else None,
    })
    return resultat


@app.get("/audio")
def audio():
    """Sert la dernière réponse vocale générée (à améliorer : vrai stockage)."""
    chemin = tts.synthetiser("")
    if chemin:
        return FileResponse(chemin, media_type="audio/wav")
    return JSONResponse(status_code=404, content={"erreur": "audio indisponible"})
