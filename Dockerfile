# ============================================================
# Wolof Services — image Docker pour Hugging Face Spaces
# Le Space écoute sur le port 7860 (imposé par HF Spaces)
# ============================================================
FROM python:3.11-slim

# Évite les caches pip inutiles dans l'image
ENV PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dépendances d'abord (meilleur cache : on ne les réinstalle
# que si requirements.txt change)
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Le code de l'API
COPY backend/ ./

# HF Spaces exige le port 7860, Render fournit le sien dans $PORT
EXPOSE 7860

# --host 0.0.0.0 : accessible depuis l'extérieur du conteneur
# ${PORT:-7860} : on suit la plateforme (Render = $PORT, HF = 7860)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-7860}"]
