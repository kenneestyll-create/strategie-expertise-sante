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
- **Design**: Tons beiges/chaleureux - Playfair Display + Manrope

## What's Been Implemented

### Phase 1 - MVP (Feb 20, 2026)
- ✅ Pages publiques (Home, About, Services, Resources, Contact)
- ✅ FAQ interactive, Formulaire contact, Panel admin JWT

### Phase 2 - Extension (Mar 12, 2026)
- ✅ Pages Tarifs, Séminaires, Entreprises, Partenaires, Avis
- ✅ Page Protection Juridique
- ✅ Système d'avis avec validation admin

### Phase 3 - Communauté (Mar 12, 2026)
- ✅ **Forum d'entraide** (/forum)
  - 6 catégories: AT, MP, Expertise, Invalidité, MDPH, Protection juridique
  - Inscription email OU anonyme (pseudonyme)
  - Création de sujets, réponses, likes, signalements
  - Badge "Anonyme" pour protéger l'identité
  - Modération admin (supprimer, bannir)
  
- ✅ **Chatbot combiné** (bouton flottant)
  - FAQ prédéfinie (6 thèmes: expertise, MDPH, AT/MP, protection juridique, tarifs, contact)
  - IA Claude Sonnet 4.5 pour questions complexes
  - Markdown rendering avec liens vers pages du site
  - Questions rapides suggérées

## Admin Credentials
- **Admin site**: admin@accompagn-sante.fr / Admin2024!
- **Forum**: Inscription utilisateur séparée

## Tarifs
- Analyse dossier: 150€+
- Préparation expertise: 250€+
- Accompagnement MDPH: 200€+
- Protection juridique: 200€+
- Accompagnement complet: 500€+ (sur devis)

## Next Tasks
- Configurer clé API Resend pour notifications email
- Ajouter mentions légales / CGU
