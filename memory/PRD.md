# Stratégie & Expertise Santé (S.E.S) — PRD

## Problème Original
Plateforme de conseil en santé : paiements sécurisés, conformité légale, stockage S3, UX fluide, SEO conversion.

## Architecture
- Frontend: React (Shadcn UI) | Backend: FastAPI + MongoDB
- Paiements: Stripe (LIVE) + PayPal (LIVE) | Stockage: AWS S3
- Email: Resend | IA: Claude Sonnet 4.5 | Recherche: Algolia | Hébergement: Vercel

## Fonctionnalités Implémentées
- [x] Stripe + PayPal Live sur TOUS les paiements (Tarifs, Agenda, Questions urgentes)
- [x] Conformité légale CGV/RGPD/L.221-28 + consent-log
- [x] AWS S3 + Admin metrics + alertes seuil
- [x] Rapport KPI hebdomadaire (Resend + APScheduler)
- [x] Scanner documents (Web Worker)
- [x] Mentions Légales (hébergeur Vercel, email définitif)
- [x] Fidélité corrigée : compteur uniquement après webhook paiement confirmé
- [x] Dashboard Admin Conseils Mascotte (CRUD + analytics)
- [x] Purge transactions (tests/tout) avec double confirmation
- [x] Comptabilité multi-périodes (jour/semaine/mois/trimestre/semestre/année)
- [x] Exit Intent Popup (mouseleave + visibilitychange)
- [x] Email unique: contact@strategie-expertise-sante.fr
- [x] Admin UI changement mot de passe + création admin secondaire
- [x] SEO Fundamentals (Title, Meta, OG, Canonical, Sitemap dynamique)
- [x] Favicon transparent SVG/PNG Shield
- [x] SEO /entreprises : contenu texte + FAQ Schema.org FAQPage
- [x] SEO /parrainage : contenu texte + FAQ Schema.org FAQPage (10% parrainage + 15% fidélité)
- [x] Fix Canonical URLs : production domain hardcodé, canonical dynamique sur toutes les pages, vercel.json trailingSlash:false
- [x] SEO /calculatrice-aah : enrichissement complet (essentiel, déconjugalisation, plafonds, cas concrets, erreurs ✗/→, 5 FAQ Schema.org, ~1000 mots)
- [x] SEO /dossier-express : description service, cible, processus + FAQ Schema.org
- [x] SEO /mdph : enrichissement complet (essentiel, certificat médical, RSDAE, enfants/mineurs, dossiers refusés, AAH+travail, invalidité vs MDPH, erreurs ✗/→, 6 FAQ Schema.org, ~1050 mots)
- [x] SEO /accident-travail-maladie-professionnelle : enrichissement complet (essentiel délais 24h/48h/120j/2ans, blocages réels, consolidation décisive, IPP capital/rente, faute inexcusable, MP hors tableau, erreurs ✗/→, 8 FAQ Schema.org sur questions Facebook réelles)
- [x] SEO /expertise-medicale : enrichissement complet (essentiel acte juridique, préparation 80%, dires contradictoires, contre-expertise, cas concret consolidation sans séquelles, 4 erreurs ✗/→, 7 FAQ Schema.org)
- [x] SEO /medecin-conseil : enrichissement complet (3 types médecins conseils CPAM/assureur/recours, convocation CPAM 6 mois, cas concret reprise imposée vs avis traitant, CRA/CMRA, invalidité vs inaptitude, 4 erreurs ✗/→, 7 FAQ Schema.org)
- [x] SEO /protection-juridique : enrichissement complet (essentiel antériorité + carence, piège souscription après litige, tableau délais de carence par domaine, audit contrats existants habitation/auto/CB premium/mutuelle, cas concret vécu "PJ découverte trop tard", 4 erreurs ✗/→, 7 FAQ Schema.org)
- [x] Encart conversion `DossierExpressCTA` : composant réutilisable élégant (barre dorée verticale + bouton outline) injecté juste avant la FAQ sur les 7 pages stratégiques (IPP, AAH, MDPH, AT/MP, Expertise, Médecin Conseil, Protection Juridique) — chaque page devient un mini-funnel d'acquisition vers /dossier-express
- [x] Audit juridique P0 : suppression des témoignages fictifs (HomePage 6 témoignages M.L./P.D./S.B./C.R./A.M./J.T. + DossierExpress 3 témoignages Marie L./Jean-Pierre D./Sophie M.) → remplacés par blocs factuels "Typologie des dossiers accompagnés" (aucun nom, aucune personne identifiable, conformité RGPD + art. L.121-2 Code consommation)
- [x] Audit juridique P0 bis : correction du libellé mensonger "cette semaine" dans les 5 compteurs publics (HomePage, DossierExpress x2, CalculatriceAAH, CalculatriceIPP) → remplacés par "accompagnés à ce jour" / "avec cet outil" (zéro risque pratique commerciale trompeuse, compteur reste ajustable via admin)
- [x] Audit juridique P0 complet : tous les faux témoignages fictifs supprimés du site (HomePage, DossierExpress, AboutPage). Credentials AboutPage alignés avec la réalité ("Dizaines de dossiers" → "Plusieurs dossiers accompagnés"). Site désormais 100% conforme art. L.121-2 Code consommation — aucun claim trompeur, aucune personne identifiable, aucune statistique inventée
- [x] Mise en conformité RGPD du formulaire /avis (art. 7 & 9 RGPD) : ajout 2 checkboxes de consentement explicite obligatoires (publication + traitement données), encart d'information RGPD (base légale, durée conservation, droits d'accès/rectification/effacement, lien politique confidentialité), label "Prénom ou pseudonyme" pour encourager pseudonymisation. Backend : rejet 422 si consentements manquants, stockage consent_date + consent_version=v1.0-2026-02 en base pour auditabilité CNIL
- [x] Encart E-E-A-T `TerrainNote` : composant réutilisable (pulse dorée + italic) injecté après la FAQ sur les 7 pages piliers avec 7 textes uniques renforçant l'ancrage terrain (compétence Google EEAT)
- [x] SEO /simulateur (landing enrichie, Option A) : Hero remplacé "Diagnostic stratégique gratuit — en 5 minutes", badge réassurance (confidentialité/sans engagement/rapport téléchargeable), CTA scroll vers formulaire, bloc "Comment ça marche" 3 étapes, bloc "Ce que vous recevez" avec mockup stylisé du rapport, 8 cartes "Pour qui" liées aux pages piliers (maillage interne), bloc confidentialité RGPD rassurant, FAQ 6 questions Schema.org + HowTo Schema.org, TerrainNote E-E-A-T final. Zéro touche au formulaire, QUESTIONS, state, axios, PDF, AdminTestBanner
- [x] /espace-client : noindex ajouté (page privée, pas d'indexation)

## SEO Phase 2 — 15 Pages Guides Actives (COMPLET)
### Bloc A — 5 Pages existantes étoffées (800-1200 mots)
1. /guide/refus-mdph-aah-que-faire (MDPH)
2. /guide/taux-ipp-5-pourcent-contester (Indemnisation)
3. /guide/expertise-medicale-defavorable-recours (Expertise)
4. /guide/accident-travail-non-declare-employeur (AT)
5. /guide/refus-maladie-professionnelle-cpam-recours (AT)

### Bloc B — 5 Nouvelles pages SEO
6. /guide/faute-inexcusable-employeur (AT)
7. /guide/inaptitude-travail-droits-recours (Emploi)
8. /guide/rente-accident-travail-calcul-contestation (Indemnisation)
9. /guide/recours-tribunal-judiciaire-pole-social (Indemnisation)
10. /guide/delai-prescription-maladie-professionnelle (AT)

### Bloc C — 5 Pages FAQ transformées en guides
11. /guide/comment-preparer-expertise-medicale (Expertise)
12. /guide/comment-demander-rqth-strategic (MDPH)
13. /guide/comment-faire-reconnaitre-maladie-professionnelle (AT)
14. /guide/maladie-professionnelle-definition-droits (AT)
15. /guide/ptia-definition-droits-strategie (Indemnisation)

### Structure de chaque page
- 6 blocs : contexte, limites, blocages, erreurs, stratégie, orientation
- Réassurance + CTA contextuel (dossier_express ou accompagnement)
- Maillage interne (2-3 liens par page)
- Schema.org FAQPage JSON-LD (2 questions/réponses par page)
- Sitemap dynamique incluant les 15 pages
- Titles SEO optimisés < 60 caractères + année automatique (GuidePage.jsx)
- Meta descriptions < 155 caractères orientées CTR
- Bloc "réponse rapide" conditionnel (4 pages à forte intention de recherche)

## En Cours / Non Terminé
- [x] Système Accès Invité VIP (token sécurisé + cookie httpOnly + bypass paiement + admin dashboard)
- [ ] P2 : Intégration HubSpot CRM (en attente identifiants)

## Guide Admin — Invités VIP

### Comment inviter un partenaire :
1. Connectez-vous à `/admin` avec vos identifiants admin
2. Cliquez sur l'onglet **"Invités VIP"** (icône bouclier dorée)
3. Cliquez **"Nouvel invité"**
4. Renseignez : **Nom complet**, **Email**, **Motif** (ex: Partenaire médical), **Durée** (90 jours par défaut)
5. Cliquez **"Créer et copier le lien"** → le lien est copié automatiquement
6. Envoyez ce lien à votre invité (WhatsApp, email, SMS)

### Ce que voit l'invité :
- Il clique sur le lien → page de connexion sécurisée
- Il saisit son email (doit correspondre exactement à celui que vous avez entré)
- Accès activé → badge "Partenaire VIP" visible → tous les services débloqués sans paiement

### Gérer les accès :
- **Désactiver** : cliquez le toggle vert → accès coupé immédiatement
- **Réactiver** : cliquez le toggle gris → accès rétabli
- **Supprimer** : cliquez la corbeille → suppression définitive
- **Copier le lien** : cliquez l'icône copie pour renvoyer le lien

### Sécurité :
- Token unique non devinable (cryptographique)
- Cookie httpOnly (non accessible par JavaScript)
- Vérification email obligatoire à chaque connexion
- Expiration automatique configurable
- Aucun accès admin pour les invités

## Backlog
- [ ] P2 : IA Prédictive V2
- [ ] P3 : Module Devis personnalisé

## Calendrier SEO — Rappels Phases
### Phase 1 (FAIT) :
- [x] Optimisation `/calculatrice-ipp` : title/H1 "Calcul IPP", barème capital 2026 vérifié, 2 cas concrets, faute inexcusable, erreurs fréquentes, 5 FAQ Schema.org (~1100 mots)
- [x] Enrichissement `/guide/refus-mdph-aah-que-faire` (cas "renouvellement AAH refusé")

### Phase 2 (MI-MAI 2026 — dans 2-3 semaines) :
- [ ] Vérifier dans Search Console : impressions "calcul IPP", "simulateur rente IPP", "renouvellement aah refusé"
- [ ] Si les positions montent → passer à Phase 3
- [ ] Si stagnation → renforcer encore les pages existantes

### Phase 3 (JUIN 2026 — après validation Phase 2) :
- [ ] Créer `/guide/tableau-57-maladie-professionnelle` (guide complet, fort potentiel)

## Credentials Admin
- Admin: admin@accompagn-sante.fr / Admin2024!
- Backup Admin: backup@strategie-expertise-sante.fr / AdminSecours2026!
- Client test: demo@test.com / Password123!
