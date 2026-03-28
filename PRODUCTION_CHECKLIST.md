# Checklist de mise en production — Stratégie & Expertise Santé

## Prérequis techniques

### 1. Hébergement
- [ ] Choisir un hébergeur (Railway, Render, VPS OVH/Hetzner, ou Emergent Deploy)
- [ ] Configurer un domaine personnalisé (ex: `strategie-expertise-sante.fr`)
- [ ] Certificat SSL (automatique avec la plupart des hébergeurs)

### 2. Base de données
- [ ] Créer un compte MongoDB Atlas (gratuit jusqu'à 512MB)
  - URL: https://cloud.mongodb.com
  - Cluster recommandé: M0 (gratuit) ou M10 (prod, ~$60/mois)
- [ ] Récupérer l'URI de connexion → `MONGO_URL`
- [ ] Configurer le nom de la base → `DB_NAME=strategie_sante`

### 3. Intelligence Artificielle
- [ ] Créer un compte Anthropic → https://console.anthropic.com
  - Récupérer la clé API → `ANTHROPIC_API_KEY`
  - Budget estimé: ~$20-50/mois selon le trafic
- [ ] (Optionnel) Créer un compte OpenAI → https://platform.openai.com
  - Récupérer la clé API → `OPENAI_API_KEY`
  - Nécessaire uniquement pour l'extraction OCR avancée

### 4. Paiements
- [ ] Créer un compte Stripe → https://dashboard.stripe.com
  - Mode test d'abord, puis activer le mode live
  - Récupérer: `STRIPE_API_KEY` (sk_live_...), `STRIPE_PUBLISHABLE_KEY` (pk_live_...)
  - Configurer le webhook → `STRIPE_WEBHOOK_SECRET`
  - URL du webhook: `https://votre-domaine.fr/api/webhook/stripe`
- [ ] (Optionnel) PayPal → `PAYPAL_CLIENT_ID`, `PAYPAL_CLIENT_SECRET`, `PAYPAL_MODE=live`

### 5. Email
- [ ] Créer un compte Resend → https://resend.com
  - Vérifier le domaine d'envoi
  - Récupérer la clé → `RESEND_API_KEY`
  - Configurer: `SENDER_EMAIL=contact@votre-domaine.fr`

### 6. Stockage fichiers
- [ ] Choisir un service S3 compatible:
  - AWS S3: https://aws.amazon.com/s3/
  - Scaleway Object Storage: https://www.scaleway.com/en/object-storage/
  - OVH Object Storage: https://www.ovhcloud.com/fr/public-cloud/object-storage/
- [ ] Créer un bucket → `S3_BUCKET`
- [ ] Récupérer les clés → `S3_ACCESS_KEY`, `S3_SECRET_KEY`
- [ ] Configurer: `S3_ENDPOINT`, `S3_REGION`

### 7. Recherche (optionnel)
- [ ] Algolia → https://www.algolia.com (gratuit jusqu'à 10k requêtes/mois)
- [ ] `ALGOLIA_APP_ID`, `ALGOLIA_API_KEY`, `ALGOLIA_INDEX_NAME`

## Variables d'environnement de production

```env
# Base
MONGO_URL=mongodb+srv://user:pass@cluster.mongodb.net/strategie_sante
DB_NAME=strategie_sante
SITE_URL=https://strategie-expertise-sante.fr
ALLOWED_ORIGINS=https://strategie-expertise-sante.fr
JWT_SECRET=<générer: openssl rand -hex 32>

# IA
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Paiements
STRIPE_API_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Email
RESEND_API_KEY=re_...
SENDER_EMAIL=contact@strategie-expertise-sante.fr
NOTIFICATION_EMAIL=admin@strategie-expertise-sante.fr

# Stockage
S3_ENDPOINT=https://s3.eu-west-3.amazonaws.com
S3_ACCESS_KEY=AKIA...
S3_SECRET_KEY=...
S3_BUCKET=ses-documents
S3_REGION=eu-west-3

# Recherche
ALGOLIA_APP_ID=...
ALGOLIA_API_KEY=...
ALGOLIA_INDEX_NAME=strategie_sante
```

## Déploiement

```bash
# 1. Cloner
git clone <repo> && cd strategie-expertise-sante

# 2. Configurer
cp backend/.env.example backend/.env   # remplir les valeurs live
cp frontend/.env.example frontend/.env # remplir les valeurs live

# 3. Lancer
docker compose up --build -d

# 4. Vérifier
curl https://votre-domaine.fr/api/health
```

## Vérifications post-déploiement
- [ ] Le site charge correctement
- [ ] Le chatbot répond (tester une question)
- [ ] L'espace admin est accessible
- [ ] Un paiement test Stripe fonctionne
- [ ] Un email est reçu après inscription
- [ ] L'upload de document fonctionne
- [ ] Le PDF se génère correctement
- [ ] Les données sont bien dans MongoDB Atlas
