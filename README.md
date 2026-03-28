# Stratégie & Expertise Santé (S.E.S)

Plateforme premium de conseil en maladies professionnelles — analyse IA, scanner de documents, dossiers experts.

## Architecture

```
frontend/          React 18 + Shadcn/UI + Tailwind CSS
backend/           FastAPI + MongoDB
backend/routes/    API REST (admin, client, IA, paiements, upload)
backend/utils/     PDF, OCR, emails, IA, stockage
```

## Prérequis

- **Node.js** 18+
- **Python** 3.11+
- **MongoDB** 7+
- **Tesseract OCR** + langue française (`tesseract-ocr-fra`)
- **Poppler** (pour `pdf2image`)

## Installation rapide (Docker)

```bash
# 1. Cloner le dépôt
git clone <votre-repo> && cd strategie-expertise-sante

# 2. Configurer les variables d'environnement
cp backend/.env.example backend/.env    # Remplir les valeurs
cp frontend/.env.example frontend/.env  # Remplir les valeurs

# 3. Lancer
docker compose up --build

# → Site accessible sur http://localhost
```

## Installation manuelle

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8001
```

### Frontend

```bash
cd frontend
yarn install
yarn start        # Dev → http://localhost:3000
yarn build        # Production → build/
```

## Variables d'environnement

Voir les fichiers `.env.example` dans `backend/` et `frontend/` pour la liste complète.

### Variables critiques

| Variable | Description |
|----------|-------------|
| `MONGO_URL` | URI MongoDB |
| `SITE_URL` | URL publique du site (emails, SEO, sitemap) |
| `REACT_APP_BACKEND_URL` | URL de l'API pour le frontend |
| `JWT_SECRET` | Clé secrète pour les tokens JWT |
| `STRIPE_API_KEY` | Clé secrète Stripe |
| `RESEND_API_KEY` | Clé API Resend (emails) |

### Intelligence Artificielle

L'IA utilise Claude (Anthropic). Deux options :
- **Sur Emergent** : variable `EMERGENT_LLM_KEY` (via `emergentintegrations`)
- **Autonome** : remplacer par le SDK `anthropic` natif avec `ANTHROPIC_API_KEY`

Le fichier à modifier : `backend/utils/chatbot.py`

### Stockage fichiers

Les documents clients uploadés sont stockés via Object Storage. Deux options :
- **Sur Emergent** : `STORAGE_URL` (via `emergentintegrations`)
- **Autonome** : remplacer par AWS S3 / Google Cloud Storage

Le fichier à modifier : `backend/utils/storage.py`

## Comptes de test

| Rôle | Email | Mot de passe |
|------|-------|-------------|
| Admin | `admin@accompagn-sante.fr` | `Admin2024!` |

## Points de vigilance

1. **Tesseract** doit être installé avec la langue française pour l'OCR
2. **MongoDB** doit être accessible avant le démarrage du backend
3. Les `.env` ne sont **jamais** committés (voir `.gitignore`)
4. Le QR code des PDFs pointe vers `strategie-expertise-sante.fr` (domaine final)
5. Le cron de purge automatique supprime les données OCR après 30 jours

## Licence

Propriétaire — Tous droits réservés.
