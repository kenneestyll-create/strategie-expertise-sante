# PRD - Accompagn'Santé

## Problem Statement Original
Application web de conseil basée sur une expérience vécue de maladie professionnelle (AT/MP) et de litiges assurantiels. Application entièrement en français.

## Architecture
- **Frontend**: React 19 + Tailwind CSS + shadcn/ui
- **Backend**: FastAPI + Motor (MongoDB async)
- **Database**: MongoDB
- **Auth**: JWT (Admin + Forum users séparés)
- **Email**: Resend (à configurer)
- **IA**: Claude Sonnet 4.5 via Emergent LLM Key
- **Paiements**: Stripe (mode test)
- **Design**: Tons beiges/chaleureux - Playfair Display + Manrope

## What's Been Implemented

### Phase 1 - MVP (Feb 20, 2026)
- Pages publiques (Home, About, Services, Resources, Contact)
- FAQ interactive, Formulaire contact, Panel admin JWT

### Phase 2 - Extension (Mar 12, 2026)
- Pages Tarifs, Séminaires, Entreprises, Partenaires, Avis
- Page Protection Juridique
- Système d'avis avec validation admin

### Phase 3 - Communauté (Mar 12, 2026)
- **Forum d'entraide** (/forum) - 6 catégories, inscription email/anonyme, likes, signalements
- **Chatbot combiné** - FAQ + Claude Sonnet 4.5 IA

### Phase 4 - Paiements & Légal (Mar 12, 2026)
- Stripe checkout pour 5 prestations sur /tarifs
- Pages Mentions Légales & CGU avec tabs (mentions, CGU, confidentialité)

### Phase 5 - Fonctionnalités avancées (Mar 12, 2026)
- **Compteur de visiteurs** sur la page d'accueil (incrémentation automatique)
- **Régimes spéciaux** (SNCF, RATP) sections sur Home + Services pages
- **Système de parrainage** (/parrainage) - génération de codes, 10% réduction filleul
- **Réduction fidélité** 15% dès la 2ème commande (détection automatique par email)
- **Réductions intégrées au paiement** - Modal avec code parrainage + détection fidélité
- **Visionneuse PDF** — Décision du Tribunal de Chartres N°23/00331 du 17/10/2025 intégrée sur page "Mon parcours" avec téléchargement
- **Fix z-index** grain texture (9999→1) pour chatbot cliquable

## Admin Credentials
- **Admin site**: admin@accompagn-sante.fr / Admin2024!
- **Forum**: Inscription utilisateur séparée

## Tarifs
- Analyse dossier: 150€+
- Préparation expertise: 250€+
- Accompagnement MDPH: 200€+
- Protection juridique: 200€+
- Accompagnement complet: 500€+ (sur devis)

## Pages & Routes
- / (Home), /a-propos, /accompagnements, /expertise-medicale
- /accident-travail-maladie-professionnelle, /mdph, /protection-juridique
- /tarifs, /seminaires, /entreprises, /partenaires
- /avis, /ressources, /contact, /mentions-legales
- /parrainage (NEW)
- /forum, /forum/inscription, /forum/connexion, /forum/categorie/:slug, /forum/sujet/:topicId, /forum/nouveau
- /admin/login, /admin

## Next Tasks
- Configurer clé API Resend pour notifications email
- Configurer Stripe clés live pour production
- Finaliser contenu Mentions Légales / CGU (adresse, nom responsable, etc.)
