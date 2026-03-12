# PRD - Accompagn'Santé

## Problem Statement Original
Application web de conseil basée sur une expérience vécue de maladie professionnelle (AT/MP) et de litiges assurantiels. Application entièrement en français.

## Architecture
- **Frontend**: React 19 + Tailwind CSS + shadcn/ui
- **Backend**: FastAPI + Motor (MongoDB async)
- **Database**: MongoDB
- **Auth**: JWT (Admin + Forum users + Clients séparés)
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
- Forum d'entraide (/forum) - 6 catégories, inscription email/anonyme, likes, signalements
- Chatbot combiné - FAQ + Claude Sonnet 4.5 IA

### Phase 4 - Paiements & Légal (Mar 12, 2026)
- Stripe checkout pour 5 prestations + 4 prestations urgentes sur /tarifs
- Pages Mentions Légales & CGU avec tabs

### Phase 5 - Fonctionnalités avancées (Mar 12, 2026)
- Compteur de visiteurs sur la page d'accueil
- Régimes spéciaux (SNCF, RATP) sections sur Home + Services
- Système de parrainage (/parrainage) - 10% réduction filleul
- Réduction fidélité 15% dès la 2ème commande
- Visionneuse PDF — Décision Tribunal de Chartres N°23/00331 du 17/10/2025
- Fix z-index grain texture

### Phase 6 - Pass Urgent & Admin Parrainage (Mar 12, 2026)
- Pass Urgent sur /tarifs — 4 forfaits prioritaires 48h (250€, 400€, 320€, 750€)
- Tableau de bord parrainage admin

### Phase 7 - Fonctionnalités majeures (Mar 12, 2026)
- **Agenda en ligne** (/agenda) — Calendrier interactif, créneaux 30min, réservation téléphone/visio
- **Simulateur de droits** (/simulateur) — Questionnaire 5 étapes avec arbre décisionnel, recommandations personnalisées
- **Espace client** (/espace-client) — Inscription/connexion, suivi de dossiers avec historique, timeline des mises à jour
- **Bibliothèque de ressources** — 6 guides PDF téléchargeables sur /ressources (AT/MP, MDPH, expertise, recours, IPP, assurance)
- **Système de relance** — Tracking paniers abandonnés, admin peut envoyer relances email
- **Admin étendu** — 5 onglets : Contacts, Avis, Parrainage, RDV, Relance

### Phase 8 - Notifications & Corrections (Mar 12, 2026)
- **Correction durée d'expérience** : 4 ans → 7 ans sur toutes les pages (Home, À propos)
- **Système de notifications client** : Cloche avec badge non lus dans l'espace client, panneau déroulant, lecture individuelle/groupée
- **Notifications automatiques** : création de dossier → notif, mise à jour statut → notif, nouveau message → notif
- **Admin étendu à 6 onglets** : ajout onglet "Clients" avec liste des clients inscrits, compteur de dossiers, bouton "Créer un dossier"

## Admin Credentials
- **Admin site**: admin@accompagn-sante.fr / Admin2024!
- **Forum**: Inscription utilisateur séparée
- **Espace client**: Inscription utilisateur séparée

## Tarifs
- Analyse dossier: 150€+ | Urgent 48h: 250€
- Préparation expertise: 250€+ | Urgent 48h: 400€
- Accompagnement MDPH: 200€+ | Urgent 48h: 320€
- Protection juridique: 200€+
- Accompagnement complet: 500€+ | Urgent 48h: 750€

## Pages & Routes
- / (Home), /a-propos, /accompagnements, /expertise-medicale
- /accident-travail-maladie-professionnelle, /mdph, /protection-juridique
- /tarifs, /seminaires, /entreprises, /partenaires
- /avis, /ressources, /contact, /mentions-legales
- /parrainage, /agenda, /simulateur, /espace-client
- /forum, /forum/inscription, /forum/connexion, /forum/categorie/:slug, /forum/sujet/:topicId, /forum/nouveau
- /admin/login, /admin

## Next Tasks
- Configurer clé API Resend pour notifications email et relances
- Configurer Stripe clés live pour production
- Finaliser contenu Mentions Légales / CGU (adresse, nom responsable, etc.)
- Créer les vrais fichiers PDF des guides téléchargeables
