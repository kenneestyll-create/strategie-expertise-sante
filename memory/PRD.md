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
