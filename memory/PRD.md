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
3. **Administrateur**: Gestionnaire des demandes de contact

## Core Requirements (Static)
- [x] Page d'accueil avec mission
- [x] Page À propos avec parcours personnel (timeline 4 ans)
- [x] Page Accompagnements (4 services)
- [x] Page Ressources avec glossaire (IPP, PTIA, CRRMP, etc.) et FAQ interactive
- [x] Page Contact avec formulaire
- [x] Panel Admin avec auth JWT
- [x] Ton humain, accessible, rassurant
- [x] Design simple, professionnel, chaleureux

## What's Been Implemented (Feb 20, 2026)
- ✅ 5 pages publiques complètes (Home, About, Services, Resources, Contact)
- ✅ FAQ interactive avec 12 questions/réponses en 4 catégories
- ✅ Formulaire de contact fonctionnel avec stockage MongoDB
- ✅ Panel admin avec login JWT et dashboard complet
- ✅ Gestion des demandes (CRUD, statuts, notes admin)
- ✅ Design beige/chaleureux avec typographie Playfair Display + Manrope
- ✅ Navigation responsive avec menu mobile
- ✅ Statistiques admin en temps réel

## Prioritized Backlog

### P0 (Critical)
- (none - MVP complete)

### P1 (Important)
- [ ] Configurer Resend avec vraie clé API pour notifications email
- [ ] Ajouter page mentions légales / politique de confidentialité

### P2 (Nice to have)
- [ ] Export CSV des demandes de contact
- [ ] Statistiques avancées (graphiques par période)
- [ ] Blog / actualités
- [ ] Multi-langue

## Next Tasks
1. Demander à l'utilisateur sa clé API Resend pour activer les notifications email
2. Affiner le contenu placeholder avec textes définitifs
3. Ajouter email/téléphone réels dans le footer
