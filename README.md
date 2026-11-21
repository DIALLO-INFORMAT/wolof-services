# 🇸🇳 Wolof Services

Plateforme de **services du quotidien en wolof** pour le Sénégal — adaptée du
projet béninois **« J'aime ma langue »** (intelligence artificielle au service
des langues locales).

> On **parle en wolof** → l'application comprend → elle donne la **météo**,
> les **prix au marché**, les **pharmacies de garde** → elle **répond en voix wolof**.

> ⚠️ Tout est **gratuit** : logiciels open source, APIs sans clé, hébergement free tier.
> **Coût total : 0 €.**

---

## ✅ Fonctionnel et testé en direct

| Service | Source | État |
|---|---|---|
| 🌦️ Météo | [Open-Meteo](https://open-meteo.com) — gratuit, sans clé | ✅ live |
| 🌾 Prix au marché | `backend/data/prix_marche.csv` | ✅ 11 produits |
| 🏥 Pharmacies | OpenStreetMap (double source + cache) | ✅ 10 à Dakar |
| 🗣️ Compréhension | Mots-clés wolof/français, accents gérés | ✅ |
| 🎙️ Voix (STT/TTS) | Whisper + Piper | ⬜ prêt à activer |
| 🤖 Questions libres | Ollama (LLM local) | ⬜ prêt à activer |

**Exemple de réponse réelle :**

```json
POST /ask  {"texte": "pharmacie de garde Dakar"}
{
  "pharmacies": [
    {"nom": "Pharmacie Stella", "lat": 14.7038, "lon": -17.4749,
     "ouverture": "Mo-Sa 08:30-20:30"},
    {"nom": "Pharmacie Kermel", "lat": 14.6701, "lon": -17.4300}
  ],
  "texte": "Farmaasi bi ci biir bi moo gën a néew : Pharmacie Stella. Dañu ko gise ci wàllu bi.",
  "intention": "sante"
}
```

---

## Architecture

```
📱 App Flutter (Android)
      │  micro : voix en wolof
      ▼
🖥️ Backend Python (FastAPI)
   1. Whisper     → voix → texte wolof      (STT)
   2. intent.py   → détecte ce que veut l'utilisateur
   3. services/   → météo · prix marché · pharmacies
   4. Piper       → texte → voix wolof       (TTS)
      │
      ▼
📱 Réponse : texte + voix
```

### Arborescence

```
wolof-services/
├── README.md                  ← ce fichier
├── .gitignore
├── backend/                   ← Python : l'IA + les services
│   ├── main.py                ← le serveur API (point d'entrée)
│   ├── requirements.txt
│   ├── config.py              ← réglages (langue, villes, modèles)
│   ├── services/
│   │   ├── stt.py             ← voix → texte (Whisper)
│   │   ├── tts.py             ← texte → voix (Piper)
│   │   ├── llm.py             ← réponse libre (Ollama, optionnel)
│   │   ├── intent.py          ← comprend la demande (mots-clés wolof/français)
│   │   ├── meteo.py           ← météo (Open-Meteo, gratuit)
│   │   ├── sante.py           ← pharmacies (OSM, 2 sources + cache)
│   │   └── marche.py          ← prix au marché (fichier local)
│   ├── data/prix_marche.csv   ← base de prix (à enrichir)
│   └── tests/                 ← 11 tests unitaires
└── mobile/                    ← Flutter : l'app Android
    ├── pubspec.yaml
    └── lib/
        ├── main.dart
        ├── screens/home_screen.dart
        └── services/api_service.dart
```

---

## 🚀 Démarrage rapide

### Étape 0 — Installer les outils (gratuits)

| Outil | Où le télécharger | Vérifier |
|---|---|---|
| **Python 3.10+** | https://python.org | `python --version` |
| **Flutter SDK** | https://docs.flutter.dev | `flutter --version` |
| **Android Studio** | https://developer.android.com/studio | émulateur / APK |
| **Ollama** (optionnel) | https://ollama.com | `ollama --version` |

> Windows : cochez **« Add Python to PATH »** à l'installation.

### Étape 1 — Lancer le backend

```powershell
cd backend
python -m venv venv
venv\Scripts\activate            # Linux/macOS : source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Ouvrez **http://127.0.0.1:8000/docs** → Swagger UI → `POST /ask` → `Try it out` :

```json
{"texte": "météo Dakar"}
```

### Étape 2 — Les tests

```powershell
python tests/test_services.py      # intention, météo, marché
python tests/test_sante_xml.py     # parseur OSM (sans réseau)
```

### Étape 3 — L'app Android

```powershell
cd mobile
flutter create .        # génère les fichiers Android manquants
flutter pub get
flutter run             # sur l'émulateur ou le téléphone connecté
```

> Téléphone : **Paramètres → À propos → Numéro de build** (7 fois) puis
> **Options pour les développeurs → Débogage USB**.
>
> Dans `lib/services/api_service.dart`, remettez l'IP de votre PC :
> `static const String baseUrl = 'http://192.168.x.x:8000';` (`ipconfig` → Adresse IPv4).
> Émulateur : `http://10.0.2.2:8000` (valeur déjà mise par défaut).

### Étape 4 — Mettre en ligne (gratuit)

| Service | Pour | Free tier |
|---|---|---|
| **Hugging Face Spaces** | Démo publique du backend | illimité (CPU) |
| **Render.com** | Backend Python | 750 h/mois |
| **Vercel / Netlify** | Site web | illimité |

---

## 🗣️ Vocabulaire de détection (à enrichir avec des locuteurs natifs)

| Service | Mots-clés reconnus |
|---|---|
| Météo | meteo, njafi, tegg, temps, temperature, abbes, pluie |
| Prix au marché | prix, marche, sokhna, kosam, combien, ndel, riz, mil, poisson |
| Santé | pharmacie, sante, malade, docteur, medecin, hopital, garde |

Réponses de base en wolof :

| Wolof | Français |
|---|---|
| **Jamm rekk** | Merci seulement |
| **Nanga def ?** | Comment allez-vous ? |
| **Jërëm-jërëm** | S'il vous plaît / Désolé |
| **Wàllu bi** | Le lieu, l'endroit |
| **Dañu ko gise** | Nous allons le trouver |
| **Farmaasi** | Pharmacie |
| **Sokhna** | Marché |

> 📌 **À faire absolument** : faites valider les mots-clés **et** les réponses
> par 2–3 locuteurs natifs avant de diffuser. L'orthographe du wolof varie
> (ñ, ŋ, accents) : le projet garde **une seule convention** — alphabet latin
> avec `ñ` et `ŋ`, gérée par `services/intent.py::normaliser()`.

---

## 🏥 Notes de terrain — Santé / pharmacies (réseau Afrique de l'Ouest)

`services/sante.py` combine **deux sources gratuites** car Overpass est capricieux :

| Source | Forces | Faiblesses constatées |
|---|---|---|
| **Overpass API** | grande zone, 1 requête | `502 at capacity`, timeouts, `406` selon le réseau |
| **API principale OSM** (`api.openstreetmap.org`) | fiable, 2-3 s | limite **50 000 nœuds** → boîte réduite |

- Les deux sont interrogées **en parallèle**, résultats **fusionnés et triés** par distance
- **Cache 1 h** en mémoire : si le réseau retombe, on ressert la dernière réponse
- En cas d'échec total : message wolof poli, **jamais de crash 500**
- Le parseur XML est couvert par `tests/test_sante_xml.py` (sans réseau)

---

## 🗺️ Roadmap

- [x] Backend FastAPI : `/health`, `/ask`, `/ask/voix`, `/audio`
- [x] Météo en direct (Open-Meteo)
- [x] Prix au marché (11 produits)
- [x] Pharmacies OSM (double source + cache + tri par distance)
- [x] Détection d'intention wolof/français + gestion des accents
- [x] 11 tests unitaires verts
- [x] Swagger UI sur http://127.0.0.1:8000/docs
- [ ] Collecte de voix en wolof (Mozilla Common Voice, enregistrements maison)
- [ ] Fine-tuning de Whisper sur le wolof
- [ ] Enregistrer une vraie voix wolof pour Piper
- [ ] Contes culturels en wolof
- [ ] Transfert d'argent (⚠️ partenariat Wave/Orange Money requis — pas d'API publique)
- [ ] Publication sur le Play Store

### Comment contribuer au wolof

1. **Enrichir les prix** : ajoutez des lignes dans `backend/data/prix_marche.csv`
2. **Enrichir le vocabulaire** : ajoutez des mots-clés dans `backend/services/intent.py`
3. **Enrichir les villes** : `backend/config.py` → `VILLES`
4. **Enregistrer votre voix** : contribuez sur [Common Voice wolof](https://commonvoice.mozilla.org)

---

## 🆓 Coût

| Poste | Coût |
|---|---|
| Modèles open source (Whisper, Piper, Llama) | 0 € |
| APIs (Open-Meteo, OpenStreetMap) | 0 € |
| Colab / Kaggle pour l'entraînement | 0 € |
| Hébergement (HF Spaces, Render, Vercel) | 0 € |
| **Total** | **0 €** |

## 📄 Licence

Code source libre — à utiliser et à améliorer librement.
