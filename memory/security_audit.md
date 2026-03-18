# Audit de Sécurité — Stratégie & Expertise Santé
## Date: 17 Mars 2026

## Résumé des 6 correctifs de sécurité

### 1. ✅ JWT Secret sécurisé (P1 - Critique)
- **Fichier:** `/app/backend/config.py` (ligne 34-36)
- **Correction:** Le secret JWT est lu depuis la variable d'environnement `JWT_SECRET`. Le serveur refuse de démarrer si la variable est absente.
- **Test:** Le serveur démarre et émet des tokens valides.

### 2. ✅ Flux de paiement sécurisé — Dossier Express (P1 - Critique)
- **Fichiers:** `/app/backend/routes/strategiia.py`, `/app/backend/routes/payments.py`
- **Correction:**
  - L'endpoint `/dossier-express/submit` vérifie le paiement dans `payment_transactions` avant de traiter le dossier.
  - Fallback avec vérification live Stripe (protège contre la race condition webhook).
  - Le webhook `/api/webhook/stripe` met à jour `payment_verified` dans `dossier_express` quand le paiement est confirmé.
  - L'analyse premium (`/api/client/dossier-analysis`) vérifie `payment_verified != false`.
- **Test:** HTTP 402 retourné quand soumission sans paiement valide.

### 3. ✅ Rate Limiting (P2 - Haute)
- **Fichiers:** `/app/backend/config.py`, `/app/backend/routes/auth.py`, `/app/backend/routes/client.py`
- **Correction:** `slowapi` appliqué sur tous les endpoints d'authentification (5/min pour login/register).
- **Test:** HTTP 429 après 6 tentatives rapides.

### 4. ✅ Uploads sécurisés (P2 - Haute)
- **Fichier:** `/app/backend/routes/client.py` (lignes 758-789)
- **Corrections:**
  - Whitelist MIME types (PDF, images, documents office, texte)
  - Whitelist extensions de fichier
  - Limite de taille 10 Mo
  - Scan de signatures dangereuses (PHP, scripts, exécutables)
- **Test:** HTTP 400 pour `.exe` / MIME non autorisé. Upload `.pdf` accepté.

### 5. ✅ Politique CORS stricte (P2 - Haute)
- **Fichier:** `/app/backend/server.py` (lignes 28-35)
- **Correction:** Origins lus depuis `ALLOWED_ORIGINS` en variable d'environnement. Pas de fallback `*`.
- **Test interne (localhost:8001):** Retourne `access-control-allow-origin: https://non-blocking-ocr.preview.emergentagent.com` ✅
- **Note:** L'ingress Kubernetes du preview override les headers CORS avec `*`. Ce comportement est propre à l'environnement de preview et n'affecte pas la production.

### 6. ✅ Accès documents sécurisé (P3 - Moyenne)
- **Fichier:** `/app/backend/routes/client.py`
- **Correction:** Tous les endpoints documents utilisent `get_current_client` (authentification) + filtre `client_id` (propriété).
- **Tests:**
  - Accès cross-utilisateur: HTTP 404 (document non trouvé pour cet utilisateur)
  - Accès non authentifié: HTTP 403
  - Admin via `/admin/documents`: protégé par `get_current_admin`

## Headers de sécurité
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: camera=(), microphone=(), geolocation=()`
