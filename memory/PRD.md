# PRD - Stratégie & Expertise Santé

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

### Phase 9 - PayPal (Mar 12, 2026)
- **PayPal Sandbox** intégré en plus de Stripe
- Modal de paiement : choix entre "Carte bancaire" (Stripe) et "PayPal"
- Backend : `/api/paypal/calculate` (calcul remises) + `/api/paypal/record` (enregistrement transaction)
- Réductions fidélité 15% et parrainage 10% appliquées aussi sur PayPal

### Phase 10 - Calculatrices & Corrections (Mar 12, 2026)
- **Calculatrice IPP** (/calculatrice-ipp) — Estimation indemnisation selon barème AT/MP, capital forfaitaire (taux <10%), rente viagère (taux >=10%)
- **Calculatrice AAH** (/calculatrice-aah) — Estimation AAH mensuelle selon taux invalidité, situation familiale, enfants, revenus. Barème 2024-2025 (max 971,37€)
- **Système de z-index centralisé** — Variables CSS --z-header, --z-dropdown, --z-modal, --z-toast, --z-chatbot dans index.css
- **Relance automatique** — Tâche de fond (toutes les 30min) pour envoi auto d'emails de relance paniers abandonnés (activé quand clé Resend configurée)
- **Placeholders Resend** — Variables RESEND_API_KEY, SENDER_EMAIL, NOTIFICATION_EMAIL ajoutées dans backend/.env
- **Partage d'estimation** — Boutons WhatsApp, SMS, Email et "Copier le lien" sur les résultats des deux calculatrices. Liens uniques avec paramètres URL pour auto-calcul à l'ouverture.
- **Compteur hebdomadaire** — "X personnes ont estimé leurs droits cette semaine" affiché sous chaque calculatrice, incrémenté à chaque calcul (backend collection calculator_usage)
- **Alerte urgente** — Bouton flottant rouge "Alerte urgente" visible sur toutes les pages (bottom-left). Modal avec 2 formules : "Sous 2h — 50€" et "Sous 30min — 80€". Formulaire rapide (nom, téléphone, email, message). Confirmation visuelle après envoi. Onglet admin "Alertes" avec badge, stats et gestion (marquer comme traité).
- **Encyclopédie Ressources** — 5 onglets encyclopédiques dans la page Ressources :
  1. Tableau officiel des 20 principales maladies professionnelles + zoom TMS (5 localisations)
  2. Reconnaissance hors tableau : voies Alinéa 3/4, conditions CRRMP, procédure 4 étapes
  3. IPP : définition complète, mécanismes d'indemnisation, 10 exemples concrets (3% à 100%)
  4. Annuaire MDPH interactif : 101 départements avec recherche, fiche complète (adresse, tél, email, site)
  5. Aides MDPH : 3 CMI, 6 types PCH (aide humaine/technique/logement/véhicule/animalière/charges), AAH, RQTH
- **Moteur de recherche global** — Barre de recherche dans le header (Ctrl+K), connecte tous les contenus : 20 tableaux MP, 5 TMS, 10 exemples IPP, 101 MDPH, aides, pages, guides, outils. Résultats catégorisés avec navigation directe.
- **Diagnostic amélioré** — Questionnaire 5 étapes avec :
  1. Collecte email avant résultats (pour suivi et CRM)
  2. Rapport PDF personnalisé téléchargeable (jsPDF, couleurs du site, en-tête S&ES)
  3. Contenu enrichi : droits potentiels, démarches prioritaires, délais importants, prestation recommandée
  4. Boutons partage WhatsApp/SMS/Email/Copier le lien
  5. HubSpot CRM prêt (placeholders HUBSPOT_PORTAL_ID + HUBSPOT_ACCESS_TOKEN dans .env)

## Admin Credentials
- **Admin site**: admin@strategie-expertise-sante.fr / Admin2024!
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
- /calculatrice-ipp, /calculatrice-aah
- /forum, /forum/inscription, /forum/connexion, /forum/categorie/:slug, /forum/sujet/:topicId, /forum/nouveau
- /admin/login, /admin

## Next Tasks
- Configurer clé API Resend pour notifications email et relances automatiques
- Configurer Stripe et PayPal clés live pour production
- Finaliser contenu Mentions Légales / CGU (adresse, nom responsable, etc.)
- Créer les vrais fichiers PDF des guides téléchargeables
