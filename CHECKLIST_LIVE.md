# CHECKLIST DE BASCULE LIVE — Strategie & Expertise Sante

> A valider point par point avant activation des paiements live.
> Chaque element doit etre coche et signe avant ouverture commerciale.

---

## A. PAIEMENT

| # | Element | Statut | Validation |
|---|---------|--------|------------|
| A1 | Cle Stripe Live configuree dans `.env` (`STRIPE_API_KEY=sk_live_...`) | [ ] | |
| A2 | Webhook Stripe Live configure vers `/api/stripe/webhook` | [ ] | |
| A3 | Paiement test reussi (session Stripe + retour succes) | [ ] | |
| A4 | Paiement annule (retour client propre, pas de dossier cree) | [ ] | |
| A5 | Paiement reussi + dossier cree en base avec `delivery_status` | [ ] | |
| A6 | Mode sandbox Stripe desactive, mode live actif | [ ] | |
| A7 | Email de confirmation Stripe bien configure | [ ] | |

## B. INTELLIGENCE ARTIFICIELLE

| # | Element | Statut | Validation |
|---|---------|--------|------------|
| B1 | Cle Anthropic Live configuree (`ANTHROPIC_API_KEY`) | [ ] | |
| B2 | Health check `/api/health/llm` retourne `operational: true` | [ ] | |
| B3 | Quota Anthropic suffisant (minimum 100 analyses) | [ ] | |
| B4 | Temps de reponse < 120 secondes sur analyse reelle | [ ] | |
| B5 | Analyse de test conforme au format V2 Premium attendu | [ ] | |
| B6 | Analyse vide/trop courte rejetee correctement | [ ] | |

## C. LIVRAISON

| # | Element | Statut | Validation |
|---|---------|--------|------------|
| C1 | Generation PDF reussie sur dossier test | [ ] | |
| C2 | PDF lisible, formatage premium, pas de corruption | [ ] | |
| C3 | Stockage S3 operationnel (upload + telechargement) | [ ] | |
| C4 | Lien de telechargement client valide et securise | [ ] | |
| C5 | Email client recu avec piece jointe PDF | [ ] | |
| C6 | Email client professionnel, pas de mention technique | [ ] | |
| C7 | Page de suivi client (`/dossier-express/suivi`) operationnelle | [ ] | |
| C8 | Pipeline complet : paiement -> analyse -> PDF -> stockage -> email | [ ] | |

## D. ADMIN

| # | Element | Statut | Validation |
|---|---------|--------|------------|
| D1 | Tableau Dossier Express affiche tous les dossiers | [ ] | |
| D2 | Badges `delivery_status` et `processing_step` visibles | [ ] | |
| D3 | Filtres (Tous/Livres/En cours/Incidents/En attente) fonctionnels | [ ] | |
| D4 | Bouton "Relancer" operationnel sur dossiers en erreur | [ ] | |
| D5 | Monitoring Live affiche les KPIs en temps reel | [ ] | |
| D6 | Mode de lancement (Ouvert/Controle/Indisponible) fonctionnel | [ ] | |
| D7 | Notifications admin recues en cas d'incident | [ ] | |

## E. EXPERIENCE CLIENT

| # | Element | Statut | Validation |
|---|---------|--------|------------|
| E1 | Checkout bloque si service IA indisponible (message premium) | [ ] | |
| E2 | Checkout bloque si mode "Indisponible" actif (message premium) | [ ] | |
| E3 | Page de traitement affiche les etapes de progression | [ ] | |
| E4 | En cas d'incident, message rassurant sans jargon technique | [ ] | |
| E5 | Page erreur premium avec reassurance client | [ ] | |
| E6 | Page de suivi client claire, humaine, premium | [ ] | |
| E7 | Aucune mention brute type "API error" / "timeout" / "failed" | [ ] | |

## F. SECURITE & INFRASTRUCTURE

| # | Element | Statut | Validation |
|---|---------|--------|------------|
| F1 | CORS restreint aux domaines de production | [ ] | |
| F2 | HTTPS actif sur tous les endpoints | [ ] | |
| F3 | JWT secret de production unique et securise | [ ] | |
| F4 | Variables `.env` de production configurees | [ ] | |
| F5 | Logs de production operationnels | [ ] | |
| F6 | Rate limiting actif | [ ] | |

---

## VERDICT FINAL

| Categorie | Status | Commentaire |
|-----------|--------|-------------|
| Paiement | | |
| IA | | |
| Livraison | | |
| Admin | | |
| Experience client | | |
| Securite | | |

**FEU VERT FINAL : [ ] OUI / [ ] NON**

Date : ___________
Signe par : ___________
