# AUDIT COMPLET — Stratégie & Expertise Santé
## Réalisé le 17 mars 2026

---

## 1. ARCHITECTURE GLOBALE

### Stack technique
| Couche | Technologie | Version |
|--------|-------------|---------|
| **Frontend** | React + Vite | React 18, Vite 5 |
| **UI** | Tailwind CSS + Shadcn/UI | Tailwind 3.4 |
| **Backend** | FastAPI (Python) | FastAPI 0.115 |
| **Base de données** | MongoDB (Motor async) | Motor 3.6 |
| **IA** | Claude Sonnet 4.5 via Emergent LLM Key | emergentintegrations |
| **Email** | Resend (sandbox) | resend 2.5 |
| **Paiements** | Stripe + PayPal | Mode test |
| **PDF** | fpdf2 + DejaVu Sans | fpdf2 2.8 |
| **OCR** | Tesseract + GPT-4o enhancement | pytesseract |
| **Stockage** | Object Storage Emergent (S3-compatible) | boto3 |
| **Scheduling** | asyncio (custom loop) | Natif Python |

### Structure des services
```
/app/
├── backend/
│   ├── server.py              # Point d'entrée FastAPI, middlewares, schedulers
│   ├── config.py              # Configuration, variables d'environnement, DB
│   ├── models.py              # Modèles Pydantic
│   ├── routes/
│   │   ├── admin.py           # 56 endpoints protégés admin (1237 lignes)
│   │   ├── client.py          # 21 endpoints protégés client (1068 lignes)
│   │   ├── strategiia.py      # 9 endpoints StratégiIA + Dossier Express (617 lignes)
│   │   ├── payments.py        # Stripe + PayPal webhooks (200 lignes)
│   │   ├── forum.py           # 14 endpoints forum (protégés)
│   │   ├── chatbot.py         # Chatbot IA
│   │   ├── public.py          # Endpoints publics (contact, newsletter)
│   │   └── misc.py            # Sitemap, config, etc.
│   └── utils/
│       ├── auth.py            # JWT, bcrypt, guards
│       ├── email.py           # Resend, templates, variables
│       ├── storage.py         # Object Storage (S3)
│       ├── ocr_gpt.py         # OCR + GPT-4o extraction
│       ├── push.py            # Web Push notifications
│       └── pdf_guides.py      # Génération PDF dynamique
└── frontend/
    ├── src/
    │   ├── pages/             # 25+ pages
    │   ├── components/        # 30+ composants
    │   └── hooks/             # Custom hooks
    └── package.json
```

### Hébergement
| Aspect | Détail |
|--------|--------|
| **Environnement actuel** | Preview Emergent (Kubernetes) |
| **URL preview** | `https://scanner-fix-5.preview.emergentagent.com` |
| **Frontend** | Port 3000 (supervisord, hot reload) |
| **Backend** | Port 8001 (supervisord, hot reload) |
| **Ingress** | Préfixe `/api` → backend:8001, reste → frontend:3000 |
| **Production** | Non déployé — nécessite configuration DNS + SSL |

### Gestion des sessions
- **JWT Bearer tokens** avec expiration configurable (`JWT_EXPIRATION_HOURS`)
- **3 types de tokens** : Admin, Client, Forum User
- **Stockage côté client** : `localStorage` (frontend)
- **Pas de refresh token** : le token expire, l'utilisateur doit se reconnecter

---

## 2. SÉCURITÉ

### 2.1 Authentification & Accès

**Gestion des comptes :**
| Rôle | Inscription | Authentification | Endpoints protégés |
|------|-------------|-----------------|-------------------|
| **Admin** | Seed automatique au démarrage | Email + mot de passe → JWT | 56 endpoints via `get_current_admin` |
| **Client** | Auto-inscription (`/api/client/register`) | Email + mot de passe → JWT | 21 endpoints via `get_current_client` |
| **Forum** | Inscription séparée | Email + mot de passe → JWT | 14 endpoints via `get_current_forum_user` |

**Hachage des mots de passe :** bcrypt (salt automatique)
**Algorithme JWT :** HS256

#### VULNÉRABILITÉS DÉTECTÉES :

| # | Sévérité | Problème | Détail |
|---|----------|----------|--------|
| V1 | **CRITIQUE** | JWT_SECRET en dur dans le code | `config.py` ligne 29 : `JWT_SECRET = os.environ.get('JWT_SECRET', 'accompagn-sante-secret-key-2024')`. Si la variable d'environnement n'est pas définie, un secret prévisible est utilisé. |
| V2 | **HAUTE** | Pas de rate limiting sur login | Aucune protection contre le brute force sur `/api/client/login`, `/api/admin/login`, `/api/forum/login`. Un attaquant peut tester des milliers de combinaisons. |
| V3 | **MOYENNE** | Pas de refresh token | Le token JWT a une durée de vie fixe. Pas de mécanisme de révocation ni de refresh. |
| V4 | **MOYENNE** | CORS `allow_origins=["*"]` | Toutes les origines sont autorisées. En production, cela doit être restreint au domaine exact. |
| V5 | **BASSE** | Admin seed en clair dans le code | Le mot de passe admin par défaut `Admin2024!` est visible dans `server.py`. |

### 2.2 Données sensibles

**Stockage des données utilisateurs :**
- MongoDB (non chiffré au repos dans l'environnement preview)
- Données personnelles : email, nom, téléphone, numéro de sécurité sociale (via OCR)
- Mots de passe : hachés avec bcrypt (sécurisé)

**Documents uploadés :**
| Aspect | État |
|--------|------|
| Stockage primaire | Object Storage S3-compatible (Emergent) |
| Fallback | Base64 en MongoDB |
| Accès | Protégé par JWT — `client_id` vérifié dans chaque requête |
| URLs directes | Non — les documents passent par `/api/client/documents/{id}/download` avec auth |
| Isolation | Chaque client ne peut accéder qu'à ses propres documents (`client_id` filter) |

#### VULNÉRABILITÉS DÉTECTÉES :

| # | Sévérité | Problème |
|---|----------|----------|
| V6 | **HAUTE** | Pas de chiffrement des données sensibles au repos (n° SS, données médicales) |
| V7 | **MOYENNE** | Les données OCR extraites (n° SS, noms, montants) sont stockées en clair dans `ocr_fields` |
| V8 | **BASSE** | Le fallback base64 en MongoDB augmente significativement la taille de la DB |

### 2.3 API & Backend

**Protection des endpoints :**
- **Admin** : 56 endpoints protégés via `Depends(get_current_admin)`
- **Client** : 21 endpoints protégés via `Depends(get_current_client)`
- **Forum** : 14 endpoints protégés via `Depends(get_current_forum_user)`
- **Public** : Contact, newsletter, StrategiIA (pas d'auth nécessaire)

**Isolation des données entre clients :**
- Chaque requête client filtre par `client_id = client["sub"]` (extrait du JWT)
- Un client A ne peut pas accéder aux documents/dossiers du client B
- Vérifié sur : documents, dossiers, analyses, notifications

#### VULNÉRABILITÉS DÉTECTÉES :

| # | Sévérité | Problème |
|---|----------|----------|
| V9 | **HAUTE** | Aucune validation des types de fichiers uploadés | Pas de whitelist MIME/extension. Un fichier `.exe` ou `.php` pourrait être uploadé |
| V10 | **HAUTE** | Pas de limite de taille de fichier côté backend | Aucun `MAX_FILE_SIZE`. Un fichier de plusieurs Go pourrait être envoyé |
| V11 | **MOYENNE** | Pas de protection CSRF | Les endpoints mutatifs (POST/PATCH/DELETE) ne vérifient pas de token CSRF |
| V12 | **BASSE** | Pas de headers de sécurité HTTP | Manque : `X-Content-Type-Options`, `X-Frame-Options`, `Strict-Transport-Security`, `Content-Security-Policy` |

### 2.4 Paiements (Dossier Express)

**Flux actuel :**
1. Client soumet le formulaire Dossier Express
2. Redirection vers Stripe Checkout (mode test) ou PayPal
3. Webhook Stripe/PayPal confirme le paiement
4. Statut du dossier mis à jour en DB

**État :**
| Aspect | État |
|--------|------|
| Stripe | Mode TEST (clé `sk_test_...`) |
| PayPal | Mode SANDBOX |
| Webhook signature | Stripe: vérifié via `stripe.Webhook.construct_event` |
| Vérification paiement | Le webhook met à jour le statut — mais pas de vérification côté client |

#### VULNÉRABILITÉS DÉTECTÉES :

| # | Sévérité | Problème |
|---|----------|----------|
| V13 | **CRITIQUE** | Le statut Dossier Express peut être "completed" sans paiement vérifié | Le backend met `status: "completed"` sur soumission du formulaire, pas uniquement après confirmation webhook. Un utilisateur pourrait accéder aux features premium sans payer. |
| V14 | **HAUTE** | Pas de vérification croisée paiement/accès | L'endpoint `dossier-analysis` vérifie `dossier_express.status == "completed"` mais ne vérifie pas qu'un paiement Stripe/PayPal associé a bien été encaissé. |

---

## 3. FONCTIONNALITÉS ACTUELLES

### 3.1 StratégiIA (GRATUIT)

| Fonctionnalité | Détail |
|----------------|--------|
| Formulaire | Type de dossier, régime, situation (texte libre) |
| Analyse IA | Claude Sonnet 4.5 — analyse textuelle |
| Email gate | L'utilisateur doit fournir son email pour voir le résultat complet |
| Résultat | Texte structuré : diagnostic, arguments, plan d'action |
| Score de pertinence | Score interne de l'analyse |
| Upsell | CTA vers rapport premium (29€) et Dossier Express (97€) |
| **Limitations** | Pas d'OCR, pas de score de solidité, pas de document upload, pas de suivi |

### 3.2 Dossier Express (PAYANT — 97€)

| Fonctionnalité | Détail |
|----------------|--------|
| Formulaire enrichi | Type, régime, situation + email, nom, téléphone |
| Upload documents + OCR | DocumentUploader avec `enableOCR=true` |
| Auto-remplissage via OCR | Type de dossier, régime, nom, situation extraits automatiquement |
| Score de solidité | Score composite 0-100 (complétude 40%, qualité 20%, cohérence, analyses, volume) |
| 3 métriques clés | Complétude, Qualité, Cohérence — toujours visibles |
| Points de fragilité | Détection automatique (documents manquants, illisibles, etc.) |
| Alertes de risque | Spécifiques par type de dossier (AT, MP, MDPH, etc.) |
| Anticipation refus | Logique prédictive avec probabilité et conséquences |
| Actions recommandées | Max 3, priorisées (haute/moyenne/faible), cliquables |
| Feedback temps réel | Toast "+X%" après upload/suppression de documents |
| Indicateur navbar | Score compact dans la barre de navigation |
| CTA Expert | Upsell vers analyse expert humaine |

### 3.3 Autres fonctionnalités

| Module | Détail |
|--------|--------|
| **Espace Client** | Dashboard, documents, notifications, profil |
| **Admin Dashboard** | 15 onglets : contacts, clients, analyses, dossiers, paiements, emails, A/B testing, forum, chatbot, calculatrices, KPIs |
| **Forum** | Inscription, catégories, sujets, réponses, modération |
| **Chatbot** | Assistant IA conversationnel |
| **Calculatrices** | IPP, AAH, simulateur |
| **Ressources** | 6 guides PDF téléchargeables |
| **Email** | Templates éditables, variables dynamiques, envoi test, campagnes programmées, A/B testing |
| **Notifications** | Push (VAPID), email (complétion 50/80/100%, relance inactivité J+7/14/21) |
| **Parrainage** | Système de codes parrainage |
| **Avis** | Collecte et affichage d'avis clients |

---

## 4. OCR & TRAITEMENT DOCUMENTS

### Pipeline OCR
```
Document uploadé (image/PDF)
    ↓
1. Extraction texte brut (Tesseract / PyPDF)
    - Images : pytesseract avec lang='fra'
    - PDF : extraction texte natif
    ↓
2. Enrichissement IA (GPT-4o via Emergent)
    - Extraction structurée : noms, dates, montants, n° SS, organisme
    - Détection type de dossier
    - Résumé et recommandations
    ↓
3. Auto-remplissage formulaire (Dossier Express)
    - type_dossier ← type_dossier_detected
    - regime ← organisme → mapping
    - name ← noms[0]
    - situation ← resume + recommandations
    ↓
4. Stockage
    - Fichier → Object Storage S3
    - Métadonnées + OCR fields → MongoDB
```

### Localisation
| Composant | Fichier |
|-----------|---------|
| OCR + GPT-4o | `/app/backend/utils/ocr_gpt.py` |
| Upload + extraction | `/app/backend/routes/client.py` (lignes 740-830) |
| Frontend uploader | `/app/frontend/src/components/DocumentUploader.jsx` |
| Scanner caméra | `/app/frontend/src/components/DocumentScanner.jsx` |

### Fiabilité estimée
| Aspect | Niveau | Commentaire |
|--------|--------|-------------|
| Extraction texte (images claires) | Bonne (80-90%) | Tesseract + français |
| Extraction texte (photos/scans) | Moyenne (60-70%) | Dépend de la qualité |
| Enrichissement GPT-4o | Bonne (85-95%) | Structuration fiable |
| Auto-remplissage | Moyenne (70-80%) | Heuristiques de mapping |

---

## 5. TESTS & ROBUSTESSE

### Tests existants
| Type | Nombre | Localisation |
|------|--------|-------------|
| Tests unitaires Python (pytest) | **210** | `/app/backend/tests/` (58 fichiers) |
| Tests d'intégration (Testing Agent) | **6 itérations** | `/app/test_reports/iteration_58-63.json` |
| Tests E2E (Playwright) | Via Testing Agent | Frontend + Backend |

### Couverture par itération
| Iteration | Scope | Backend | Frontend | Résultat |
|-----------|-------|---------|----------|----------|
| 58 | Phase 1 (Score, alertes) | 14/14 | 12/12 | 100% |
| 59 | Navbar score | 3/3 | 16/16 | 100% |
| 60 | Phase 2+3 (Actions, prédictions, premium) | 21/21 | 22/22 | 100% |
| 61 | Métriques, priorités | 15/15 | 16/16 | 100% |
| 62 | Séparation free/premium | 18/18 | 17/17 | 100% |
| 63 | OCR + régression | 18/18 | 19/19 | 100% |

### Gestion des erreurs
| Aspect | État |
|--------|------|
| Backend : try/catch sur routes | Présent sur la plupart des endpoints |
| Frontend : error boundaries | Non implémenté |
| API : codes HTTP corrects | 401 (non auth), 404 (non trouvé), 500 (erreur serveur) |
| Logging | Python `logging` — stdout/stderr vers supervisord |
| Monitoring | Non implémenté |

---

## 6. VULNÉRABILITÉS — RÉCAPITULATIF PRIORISÉ

### CRITIQUES (à corriger avant production)
| # | Problème | Impact | Correction |
|---|----------|--------|------------|
| **V1** | JWT_SECRET hardcodé en fallback | Un attaquant peut forger des tokens JWT | Définir `JWT_SECRET` en variable d'environnement, supprimer le fallback |
| **V13** | Accès premium sans paiement vérifié | Perte de revenus, contournement du paywall | Ne mettre `status: "completed"` qu'après confirmation webhook Stripe/PayPal |

### HAUTES (à corriger rapidement)
| # | Problème | Impact | Correction |
|---|----------|--------|------------|
| **V2** | Pas de rate limiting | Brute force possible sur login | Ajouter `slowapi` ou `fastapi-limiter` (ex: 5 tentatives/min) |
| **V6** | Données médicales non chiffrées au repos | Non-conformité RGPD/santé | Chiffrer les champs sensibles (n° SS, données médicales) |
| **V9** | Pas de validation type de fichier | Upload de fichiers malveillants | Whitelist MIME : `image/*, application/pdf, text/*` |
| **V10** | Pas de limite taille fichier | DoS par upload massif | Ajouter `MAX_FILE_SIZE = 10MB` côté backend |
| **V14** | Pas de vérification croisée paiement | Accès premium frauduleux | Vérifier `payment_intent.status == "succeeded"` via Stripe API |

### MOYENNES
| # | Problème | Correction |
|---|----------|------------|
| **V4** | CORS `*` | Restreindre à votre domaine production |
| **V7** | OCR data en clair | Chiffrer `ocr_fields` contenant des données sensibles |
| **V11** | Pas de CSRF | Ajouter des tokens CSRF pour les formulaires mutants |
| **V3** | Pas de refresh token | Implémenter un système refresh/access token |

### BASSES
| # | Problème | Correction |
|---|----------|------------|
| **V5** | Admin seed en clair | Utiliser une variable d'environnement pour le mot de passe initial |
| **V8** | Fallback base64 en DB | Migrer vers Object Storage exclusif |
| **V12** | Headers sécurité manquants | Ajouter via middleware : `X-Content-Type-Options`, `X-Frame-Options`, `HSTS`, `CSP` |

---

## 7. RECOMMANDATIONS

### Corrections urgentes (avant production)
1. **Sécuriser le JWT_SECRET** : variable d'environnement obligatoire, pas de fallback
2. **Verrouiller le flux de paiement** : `status: "completed"` uniquement après webhook vérifié
3. **Ajouter le rate limiting** sur les endpoints d'authentification
4. **Valider les fichiers uploadés** : whitelist MIME + limite de taille
5. **Restreindre CORS** au domaine de production

### Améliorations prioritaires
6. **Chiffrement des données sensibles** au repos (RGPD santé)
7. **Headers de sécurité HTTP** (CSP, HSTS, X-Frame-Options)
8. **Error boundaries React** côté frontend
9. **Monitoring et alertes** (erreurs, tentatives d'accès, uploads suspects)
10. **Refresh tokens** pour améliorer l'expérience utilisateur

### Optimisations techniques
11. **Refactoring** : `AdminDashboard.jsx` (2698 lignes) → découper en sous-composants
12. **Refactoring** : `EmailTemplateEditor.jsx` (821 lignes) → idem
13. **Tests de charge** : valider le comportement sous stress
14. **Backup MongoDB** : automatiser les sauvegardes
15. **CI/CD** : pipeline de tests automatisés avant déploiement

---

## CONCLUSION

**Ce qui est réellement en place :** Une application complète et fonctionnelle avec authentification, analyse IA, OCR, paiements (test), email, forum, et un système de scoring sophistiqué. L'architecture est saine et bien structurée.

**Ce qui est sécurisé :** L'isolation des données entre clients (chaque requête vérifie le `client_id`), le hachage des mots de passe (bcrypt), la protection des endpoints par JWT, et l'accès aux documents via des routes authentifiées.

**Ce qui doit être corrigé avant production :** Le JWT_SECRET hardcodé (V1), le flux de paiement non vérifié (V13/V14), l'absence de rate limiting (V2), et la validation des fichiers uploadés (V9/V10). Ces 5 points sont les priorités absolues.
