# PRD - Accompagn'Santé

## Problem Statement Original
Application web de conseil basée sur une expérience vécue de maladie professionnelle (AT/MP) et de litiges assurantiels. Application entièrement en français avec pages : Accueil, À propos, Accompagnements, Ressources, Contact. FAQ interactive. Panel admin JWT.

## Architecture
- **Frontend**: React 19 + Tailwind CSS + shadcn/ui
- **Backend**: FastAPI + Motor (MongoDB async)
- **Database**: MongoDB
- **Auth**: JWT (PyJWT + bcrypt)
- **Email**: Resend (notification à configurer)
- **Design**: Tons beiges/chaleureux - Playfair Display + Manrope fonts

## User Personas
1. **Victime AT/MP**: Personne en situation de maladie professionnelle ou accident du travail cherchant aide et informations
2. **Assuré en litige**: Personne ayant des difficultés avec son assurance prévoyance
3. **Entreprise/RH**: Structure cherchant formation et sensibilisation AT/MP
4. **Administrateur**: Gestionnaire des demandes de contact et avis

## Core Requirements (Static)
- [x] Page d'accueil avec mission + positionnement innovant
- [x] Page À propos avec parcours personnel (timeline 4 ans)
- [x] Page Accompagnements (4 services)
- [x] Page Expertise médicale
- [x] Page Accident du travail / Maladie professionnelle
- [x] Page MDPH
- [x] Page Séminaires et formations
- [x] Page Conseil aux entreprises
- [x] Page Tarifs (grille tarifaire)
- [x] Page Partenaires (réseau professionnel)
- [x] Page Avis / Livre d'or (témoignages avec validation)
- [x] Page Ressources avec glossaire et FAQ interactive
- [x] Page Contact avec formulaire
- [x] Panel Admin avec auth JWT
- [x] Ton humain, accessible, rassurant
- [x] Design simple, professionnel, chaleureux

## What's Been Implemented (Mar 12, 2026)

### Phase 1 - MVP (Feb 20, 2026)
- ✅ 5 pages publiques (Home, About, Services, Resources, Contact)
- ✅ FAQ interactive 12 questions en 4 catégories
- ✅ Formulaire de contact + stockage MongoDB
- ✅ Panel admin JWT + dashboard

### Phase 2 - Extension (Mar 12, 2026)
- ✅ Page Tarifs avec 6 prestations (4 particuliers + 2 pro)
- ✅ Page Séminaires et formations
- ✅ Page Conseil aux entreprises
- ✅ Page Partenaires (réseau de 6 types de professionnels)
- ✅ Page Avis/Livre d'or avec notation étoiles + validation admin
- ✅ Section "Approche innovante" sur page d'accueil
- ✅ Section "Réseau partenaires" sur page d'accueil
- ✅ Badge "Service pionnier en France" sur hero
- ✅ Navigation avec dropdowns (Expertises, Services)
- ✅ Admin: onglet Avis pour modération témoignages

## Prioritized Backlog

### P0 (Critical) - Fonctionnalités Phase 3
- [ ] Forum d'entraide (création sujets, réponses, modération, anonymat)
- [ ] Chatbot IA combiné (FAQ + GPT pour questions complexes)

### P1 (Important)
- [ ] Configurer Resend avec vraie clé API pour notifications email
- [ ] Mentions légales / politique de confidentialité

### P2 (Nice to have)
- [ ] Export CSV des demandes de contact
- [ ] Blog / actualités
- [ ] Multi-langue

## Tarifs (à afficher)
- Analyse de dossier: à partir de 150€
- Préparation expertise: à partir de 250€
- Accompagnement MDPH: à partir de 200€
- Accompagnement complet: à partir de 500€ (sur devis)
- Séminaires: Sur devis
- Conseil entreprises: Sur devis

## Admin Credentials
- Email: admin@accompagn-sante.fr
- Password: Admin2024!

## Next Tasks
1. Forum d'entraide avec inscription email/pseudonyme anonyme
2. Chatbot combiné FAQ + IA
3. Clé API Resend pour notifications email
