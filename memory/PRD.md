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
- [x] Email Dossier Express : ajout d'un bloc discret "Partagez votre expérience" avec lien vers /avis?source=dossier_express dans le template HTML de livraison du rapport. Mention "Témoignage anonyme possible — votre retour aide d'autres personnes" pour encourager la collecte de vrais avis conformes RGPD (complément naturel de la conformité du formulaire /avis)
- [x] Infrastructure email Resend : domaine strategie-expertise-sante.fr vérifié (DNS DKIM + SPF + DMARC sur OVH), SENDER_EMAIL/NOTIFICATION_EMAIL passés de "onboarding@resend.dev" (sandbox) à "contact@strategie-expertise-sante.fr". Test d'envoi réussi (Resend ID: ee397574). Tous les emails automatiques (Dossier Express, relances inactivité 3 niveaux, guide followups, weekly reports) partent désormais en production
- [x] PDF Auto-diagnostic : ajout du QR code en pied de document (cohérence visuelle avec PDFs Dossier Express et StrategiIA). Lib qrcode npm installée, génération frontend (jsPDF), URL `?via=qr&source=auto_diagnostic` pour tracking distinct, design identique (22mm, #1a1a1a sur #FAF8F3, libellé "Prochaine étape recommandée" + "Scanner pour prendre contact", ligne séparatrice or, fallback silencieux si lib échoue)
- [x] Indicateur Tracking QR dans Admin Dashboard : nouvel endpoint `/api/admin/contacts/qr-stats` (aggregation MongoDB par source), composant `AdminQRStats` injecté en tête du tab Contacts, affichage différencié selon état (compteur ou message d'attente), libellés humains pour les 3 sources (Dossier Express IA, StratégiIA, Auto-diagnostic). Tuto admin AdminHelpPanel enrichi d'une étape "Tracking QR" avec mots-clés de recherche (qr, qr code, tracking, pdf)
- [x] Encart E-E-A-T `TerrainNote` : composant réutilisable (pulse dorée + italic) injecté après la FAQ sur les 7 pages piliers avec 7 textes uniques renforçant l'ancrage terrain (compétence Google EEAT)
- [x] SEO /simulateur (landing enrichie, Option A) : Hero remplacé "Diagnostic stratégique gratuit — en 5 minutes", badge réassurance (confidentialité/sans engagement/rapport téléchargeable), CTA scroll vers formulaire, bloc "Comment ça marche" 3 étapes, bloc "Ce que vous recevez" avec mockup stylisé du rapport, 8 cartes "Pour qui" liées aux pages piliers (maillage interne), bloc confidentialité RGPD rassurant, FAQ 6 questions Schema.org + HowTo Schema.org, TerrainNote E-E-A-T final. Zéro touche au formulaire, QUESTIONS, state, axios, PDF, AdminTestBanner
- [x] /espace-client : noindex ajouté (page privée, pas d'indexation)
- [x] Forum — Nettoyage chirurgical de la DB (03/05/2026) : 52 topics, 18 replies, 18 reports et 140 users pytest supprimés via script ciblé (`/app/backend/cleanup_forum_pytest_data.py`). Aucune régression (100% des entrées étaient pytest, aucun vrai utilisateur). Collections `forum_topics`, `forum_replies`, `forum_users`, `forum_reports` remises à 0.
- [x] Forum — Prévention récurrence : `/app/backend/tests/conftest.py` enrichi d'une fixture session-scoped autouse `_cleanup_pytest_db_artifacts` qui scrubbe la DB en fin de session (topics/replies/reports/users pytest + clients test). Fixtures `forum_user` et `test_client_user` trackent chaque création pour cascade delete garantie. Vérifié : après un run `pytest tests/test_module_routes_forum.py`, les 4 collections retombent à 0.
- [x] Forum — Seed éditorial admin (03/05/2026) : nouveau tab "Forum" dans l'Admin Dashboard permettant de publier des **sujets graines** signés « Équipe S.E.S » sans passer par l'inscription publique. Endpoints backend : `POST /api/admin/forum/seed-topic` (création, is_pinned par défaut), `GET /api/admin/forum/seed-topics` (liste des sujets éditoriaux, author_id=admin-seed-ses), `PATCH /api/admin/forum/topics/{id}/pin` (épingler/désépingler). Composant `AdminForumSeed.jsx` : formulaire (catégorie / signature / titre / contenu ≥ 80 car. / épinglage) + liste des sujets publiés avec actions (pin/unpin, voir sur le forum, supprimer). Flag `is_seed=true` + `seeded_by` stockés pour traçabilité. Tuto admin enrichi d'une section dédiée (8 étapes, mots-clés : forum, graine, seed, épingler, éditorial, équipe ses, modération, discussion, topic).
- [x] Forum — Nettoyage pytest DB prod (03/05/2026, Option A sécurisée) : endpoints `GET /api/admin/forum/cleanup-pytest-preview` (dry-run sans modification, retourne counts + samples users/topics) et `POST /api/admin/forum/cleanup-pytest?confirm=NETTOYER` (protégé par token admin + double confirmation). Logique de détection : regex pseudos (`pytest-`, `TestUser\d+`, `AnonUser\d+`, `anon-`, `integ-`), regex emails (`@test.com`, `@example.com`, `pytest-.*@`), marqueurs titres/contenus/reasons exacts. Cascade : topics par auteurs pytest + titres marqueurs → replies (auteurs + contenus + orphan de topics supprimés) → reports (reporters + reasons + target topic pytest) → users pytest. Opération **idempotente** (relance = 0 suppression) et **chirurgicale** (vrai post "MarieP - Ma vraie question MDPH" intact après test E2E). UI : nouvelle carte dans le tab Forum admin avec bouton "Analyser la base" (affiche aperçu détaillé), bouton "Supprimer X entrées pytest" apparaît uniquement si > 0, Dialog de confirmation avec saisie obligatoire du mot "NETTOYER". Tuto admin enrichi (étape "Nettoyage pytest (si besoin)" + mots-clés : pytest, nettoyage, test, pollution, cleanup, discussions récentes). **Fix du problème visible sur strategie-expertise-sante.fr/forum** : une fois déployé via GitHub → Vercel, l'admin clique le bouton une fois et les posts pytest disparaissent de la prod.
- [x] **Straté · Conciergerie IA** (03/05/2026) : transformation du chatbot en réceptionniste IA orienté conversion. **Backend** : nouveau router `routes/strate.py` (zéro impact sur `utils/chatbot.py` gelé) + `utils/strate_prompts.py` (12 IDs de qualification sur 3 catégories AT-MP/MDPH/Expertise + branche "Autre situation" avec détection IA Claude Haiku 4.5 retournant JSON contraint). Endpoints : `POST /api/strate/chat` (flux structuré greeting → qualify → route, hard-limit 60 mots, kill-switch 503 si désactivé), `GET /api/strate/config` (public), `POST /api/admin/strate/toggle` (kill switch admin), `GET /api/admin/strate/kpis?period=7d|30d|all` (taux ouverture / qualification / **routage** + breakdown par src + opens per page). Collections MongoDB : `strate_sessions` + `strate_events` + `strate_config`. Détection données sensibles (cancer, métastase, NIR…) → step `sensitive` + redirection RDV. **Frontend** : `ChatBot.jsx` enrichi chirurgicalement (zone mobile gelée intacte) avec mode Straté complet : header "Straté · Conciergerie IA", lien permanent "Besoin d'un humain ? Parler à un expert", bandeau RGPD à chaque ouverture, message d'accueil + 4 boutons de routage, qualification 4 boutons, CTAs finaux (1 primaire doré + 1 alternative + bouton recommencer), saisie libre pour "Autre situation" avec confirmation par 3 options détectées. Hook `useStrateTriggers.js` : auto-ouverture sur scroll ≥ 40% OU 15s d'inactivité, limitée à 1 fois / 24h via `localStorage`, désactivée si focus input/textarea (tunnels en cours), désactivée sur StratégiIA / Dossier Express / Simulateur / admin / pages légales. Composant `AdminStrateKpis.jsx` dans Analytique → nouveau sous-onglet "Conciergerie Straté" avec 4 KPI cards, période 7d/30d/all, breakdown du routage par src, opens per page, kill switch ON/OFF immédiat. Tuto admin enrichi (8 étapes + 16 mots-clés). **Tests E2E curl** : flow complet greeting → qualify → route → click validé, KPIs corrects, kill switch fonctionnel (503), free-text "AAH refusée" → suggère mdph_refus/mdph_recours, free-text "dentiste" → out_of_scope, mot "cancer" → step sensitive. UI screenshot validé.
- [x] **Lead Magnet pages piliers** (04/05/2026) : capture d'emails sur les 5 pages SEO stratégiques pour amorcer la base contacts (visiteurs SEO actuels = 31 clics, 0 conversion → besoin de capter avant qu'ils disparaissent). **Backend** : nouveau `routes/leads_pillar.py` isolé. Endpoints : `POST /api/leads/pillar-subscribe` (email + page_id + consent RGPD obligatoire, idempotence 7j, envoi automatique du mémo via Resend), `GET /api/leads/pillar-magnets` (liste publique des 5 mémos), `GET /api/admin/leads/pillar-stats` (total, sent, last_7d, breakdown par page, 50 derniers leads). Collection MongoDB : `pillar_leads` avec consent_date, consent_version v1.0, ip_hint partielle pour preuve RGPD. 5 mémos rédigés inline (pas de PDF à générer) : MDPH (5 erreurs perte 6 mois), AT/MP (7 réflexes 48h), Expertise (phrase à NE JAMAIS dire), IPP (calcul réel + marges), AAH (décrypter refus + RAPO). Email HTML premium avec branding S.E.S, 3 CTAs (auto-diagnostic gratuit / CTA principal page / RDV humain). **Frontend** : composant `PillarLeadMagnet.jsx` réutilisable (premium-dark gradient, bouton or, validation email + RGPD, état succès). Injecté chirurgicalement sur `MDPHPage.jsx`, `AccidentTravailPage.jsx`, `ExpertiseMedicalePage.jsx`, `CalculatriceIPPPage.jsx`, `CalculatriceAAHPage.jsx` juste avant le `DossierExpressCTA` (capture les visiteurs pas encore prêts à convertir). Composant `AdminPillarLeads.jsx` dans Analytique → nouveau sous-onglet "Leads SEO" avec 4 KPI cards, breakdown par page, table des 50 derniers leads. Tuto admin enrichi (7 étapes + 16 mots-clés). **Tests E2E** : subscribe valide → email Resend envoyé ✅ ; sans consent → 400 ✅ ; bad email → 400 ✅ ; bad page_id → 400 ✅ ; idempotence 7j (already_subscribed=true) ✅ ; admin stats affichées correctement ✅ ; UI screenshot MDPH validée (zone Hero gelée intacte). Objectif initial : 0 → 5-10 emails captés en 4-6 semaines.
- [x] **Studio Éditorial S.E.S** (04/05/2026) : système de production de guides SEO premium avec IA contrainte + 7 garde-fous + validation ciblée. **Backend** : nouveau `routes/editorial.py` (820 lignes) + `utils/editorial_seed_data.py` (22 références légales pré-vérifiées : CSS L.821-1/2, L.411-1, L.461-1, L.452-1, R.441-7, L.141-1, jurisprudences amiante 2002 + burnout 2010, chiffres AAH/PASS, délais RAPO/recours/déclaration AT/dires, barème IPP — 30 sujets pré-classés par potentiel SEO sur AT/MP, MDPH, Expertise, Invalidité, IPP, AAH). Endpoints (16) : start article (pool ou custom), generate-plan (Claude Haiku JSON contraint, 3000 tokens), generate-draft (parallélisé, ~10s pour 7 sections + FAQ), red-flags scanner auto (lois, jurisprudences, chiffres, délais, médical sensible, noms propres), validate-flag, save (snapshot versions), publish (bloqué tant que tous flags non validés), perf manuelle, revalidation 6 mois, legal-refs CRUD, config toggles. Collections : `editorial_articles`, `editorial_legal_refs`, `editorial_topics`, `editorial_config`. Claude Haiku 4.5 via Anthropic API (~3-5€/mois pour 4 articles/mois). **Frontend** : composant `AdminEditorialStudio.jsx` (~600 lignes, 3 vues : home + editor + settings). Home : header + bandeau rappel hebdo + bandeau revalidation 6 mois + 5 KPIs + 3 propositions re-tirables + pool complet + custom topic + liste articles. Editor : 4 tabs (Contenu / À valider / Méta / Perf), génération plan + draft, éditeur Markdown, validation chirurgicale par drapeau (bouton "Vérifier" → Légifrance/service-public, bouton "Valider"), bouton publication grisé tant que non-validé. Settings : 2 toggles dormants (RAG live web + Génération dynamique sujets) + visualisation base légale 22 entrées. Nouveau tab "Studio" dans AdminDashboard (icône Sparkles dorée). Tuto admin enrichi (11 étapes + 24 mots-clés). **Tests E2E** : seed auto idempotent ✅ ; 3 propositions retournées ✅ ; plan IA généré (7 sections + 8 FAQ + slug + meta 132 car.) ✅ ; draft IA en parallèle 9.9s pour 20881 caractères ✅ ; 25 drapeaux rouges détectés (loi/chiffre/délai) ✅ ; publish refusé si flags non validés (400) ✅ ; UI screenshot Studio Home validée. Coût récurrent : ~3-5€/mois total (toggles dormants restent à 0€). Pool 30 sujets, 22 références légales pré-chargées au boot.

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

## Studio Éditorial — Changelog
### 2026-05-04 — Hardening + Publish Bridge (v1.1)
- [x] Prompt `SYSTEM_PROMPT_DRAFT` renforcé : interdiction % inventés, hooks ASCII fermés, fin de phrase obligatoire, longueur stricte 250-380 mots
- [x] Garde-fou juridique inline : silence MDPH = rejet (jamais acceptation), RSDAE ≥ 1 an (pas 5), délais RAPO/pôle social, seuil IPP 10 %
- [x] `max_tokens` 900 → 1400 pour éviter les sections tronquées
- [x] Post-check + auto-retry des sections défaillantes (hook non fermé, clé non-ASCII, fin abrupte, trop courte)
- [x] `/publish` branché sur collection `seo_pages` → l'article publié apparaît automatiquement sur `/guide/{slug}`
- [x] `GuidePage.jsx` rend désormais `content.markdown_body` via react-markdown (prose styling aligné sur l'identité du site)

## StrategiIA + Dossier Express IA — Hardening juridique (v1.1)
### 2026-05-04 — Protection juridique totale des prompts IA
- [x] **Suppression des jurisprudences non sourcées** (Cass. 2e civ. 2022 silence CPAM, CE 2018 MDPH, Cass. 2e civ. 2020/2021 sans n° pourvoi) dans `STRATEGIIA_SYSTEM_PROMPT`, `DOSSIER_EXPRESS_SYSTEM_PROMPT` et `utils/llm.py` SYSTEM
- [x] **Remplacement par articles de loi vérifiés** : L.411-1, L.461-1, L.452-1, L.431-1, L.434-2, R.441-10 CSS (AT/MP) ; L.821-1, L.821-2 CSS + L.114-1 CASF (AAH) ; L.141-1, R.141-1, L.142-4, L.142-8 CSS (expertise + recours)
- [x] **Statistiques CNAM brutes retirées** (87% TMS, 9/14% IPP, 35/45% contentieux, 60% faute inexcusable) → remplacées par ordres de grandeur avec réserve obligatoire "selon les données publiques CNAM/CNSA, à actualiser"
- [x] **Fourchettes d'indemnisation IP supprimées** (15k-100k€+) → remplacées par "montants variables selon la jurisprudence et les justificatifs — à évaluer au cas par cas"
- [x] **Bloc CONNAISSANCES JURIDIQUES CRITIQUES À NE JAMAIS INVERSER** ajouté : silence MDPH = rejet, RSDAE ≥ 1 an, CE non compétent MDPH, silence CPAM AT/MP conditionné à dossier complet, IPP 10%, AT 48h
- [x] **GARDE-FOU ANTI-HALLUCINATION TOLÉRANCE ZÉRO** : jurisprudence uniquement avec référence exacte (juridiction + date + n° pourvoi), sinon "selon la jurisprudence constante" ou omission ; interdiction formelle d'inventer article, décret, %, montant, barème, nom propre

### 2026-05-04 — Trust Badge "Analyse IA — Références juridiques vérifiées" (v1.2)
- [x] Badge sobre ajouté dans `utils/pdf.py` entre le CTA "Vous souhaitez aller plus loin ?" et le QR code, sur tous les rapports StrategiIA et Dossier Express IA
- [x] Visuel harmonisé : même largeur que le CTA, fond ivoire chaud, barre verticale 2mm en accent service (or pour StrategiIA, bleu marine pour Dossier Express), titre bold + sous-titre italique muted
- [x] Texte : "Analyse IA — Références juridiques vérifiées" + "Rapport appuyé sur des articles de loi officiels (Code de la Sécurité Sociale, CASF). Aucune jurisprudence citée sans référence exacte — outil d'aide à la décision."
- [x] Sécurité visuelle : gestion automatique du saut de page si espace insuffisant pour badge + séparateur + QR + ligne contact

### 2026-05-04 — Trust Badge Variante B "Contenu juridique vérifié — Sources officielles" (v1.3)
- [x] **Badge harmonisé sur les 7 PDF non-IA restants** : 6 guides PDF (`pdf_guides.py` → guide_mp, guide_expertise, guide_mdph, guide_recours, guide_ipp, guide_assurance) + auto-diagnostic Simulateur (`SimulateurPage.jsx` jsPDF)
- [x] **Variante B — texte juridiquement honnête** : "Contenu juridique vérifié — Sources officielles" / "Document rédigé par les experts S.E.S à partir des textes légaux en vigueur (Code de la Sécurité Sociale, CASF, Service-public.fr). Outil d'aide à la décision — ne remplace pas un avis personnalisé."
- [x] **Visuel identique à la Variante A** : même fond ivoire chaud, même barre verticale or 2mm, même typographie, même placement (entre la signature/CTA et le QR code ou la mention de fermeture)
- [x] **Cohérence totale 10/10 PDF** : tous les documents générés par le site portent désormais un badge harmonisé adapté à leur nature (IA vs rédaction manuelle)
- [x] Vérification visuelle automatisée à 100 % de confiance sur guide_mp (badge bien positionné, sources mentionnées, harmonie typographique préservée)

### 2026-05-04 — Auto-seed des pages SEO au déploiement (v1.4)
- [x] **Article `refus-aah-rsdae-non-reconnue` ajouté au fichier `seed_seo_pages.py`** (devient la 16e page du seed)
- [x] **Hook startup `seed_missing_only(db)`** dans `server.py` : à chaque démarrage backend, vérifie chaque slug du seed et n'insère QUE les manquants — n'écrase JAMAIS les pages existantes (préserve views, cta_clicks, conversions, modifications manuelles)
- [x] **Test de bout en bout** : suppression de l'article, redémarrage backend → log `SEO auto-seed: 1 new page(s) inserted (15 already present, 16 total in seed)` → article auto-recréé, pages existantes intactes
- [x] **Méthode définitive pour les pages futures** : ajout au seed → Deploy → article live en prod, sans script ni intervention manuelle

### 2026-05-04 — Studio Éditorial v2 : Structurer + Aperçu + Migrate-to-seed (v1.5)
- [x] **Phase 1 — UX critique** : 3 nouveaux boutons dans l'éditeur Studio
  - 🗑️ **Supprimer** (`hardDelete`) : suppression définitive du brouillon + restauration auto du sujet dans le pool
  - ↩️ **Changer de sujet** (`changeTopic`) : abandon du brouillon + restauration sujet + retour à l'écran de choix
  - 📥 **Archiver** : refait pour restaurer le sujet (était un soft-delete simple avant)
- [x] **Phase 2 — Output structuré identique aux articles manuels** :
  - Nouveau composant partagé `GuidePreviewBody.jsx` utilisé à la fois par `/guide/{slug}` (public) ET par le Studio admin (preview modal) → **garantit pixel-perfect parity**
  - `GuidePage.jsx` refactorisé pour utiliser `GuidePreviewBody` → **upgrade bonus** : la FAQ est désormais visible sur les pages déployées (auparavant seulement Schema.org)
  - Nouvel endpoint `POST /admin/editorial/articles/{id}/structure` : 2e passe IA qui transforme le markdown en JSON structuré (reponse_rapide, contexte, limites, blocages[], erreurs[], strategie, orientation[], reassurance, maillage[], faq[])
  - Parser JSON tolérant via `json_repair` (gère virgules traînantes, échappements imparfaits) — installé dans requirements.txt
  - Nouvel onglet **"Structurer"** dans l'éditeur avec formulaires admin pour éditer chaque bloc librement
  - Bouton **"Aperçu Web"** ouvre une modal plein écran qui rend le contenu structuré exactement comme la page déployée
- [x] **Phase 3 — Bridge Publish → seed_seo_pages.py (production)** :
  - Nouvel endpoint `POST /admin/editorial/articles/{id}/migrate-to-seed` qui écrit programmatiquement l'article structuré dans `seed_seo_pages.py` (devant le marqueur `]\n\nasync def seed():`)
  - Bouton **"Migrer vers production"** (vert) actif uniquement après structure + validation des red flags
  - Vérification d'unicité de slug + validation flags + JSON-safe escaping
  - Workflow définitif : Studio → Migrer → Save to GitHub → Deploy → article live sur strategie-expertise-sante.fr en ~30 sec
  - **Roue de secours préservée** : la méthode manuelle (édition directe du seed via agent) reste 100 % opérationnelle, idempotente
- [x] **Phase Bonus — Tutoriel admin mis à jour** dans `AdminHelpPanel.jsx` : 13 étapes au lieu de 9, intégrant Structurer / Aperçu Web / Migrer + Roue de secours + nouvelles actions de suppression
- [x] **2026-02-XX — Bloc B Organigramme IA** : nouveau composant `AdminAgentsOrg.jsx` + endpoint `GET /api/admin/agents/registry` (`backend/routes/agents_registry.py`). Cartographie visuelle 3 niveaux (PDG → Straté/StratégiIA/Dossier Express → Planner/Writer/Critic/Structurer). Modal détail avec mission, modèle, garde-fous et prompt système (lecture seule, copy-to-clipboard). Onglet "Organigramme IA" dans Admin Dashboard.
- [x] **2026-02-XX — Bloc C Tutoriel Studio mis à jour 14 étapes** : Studio Éditorial passe de 13 à 14 étapes intégrant le nouveau Critic juridique (architecture multi-agents Planner → Writer → Critic → Structurer). Ajout d'une nouvelle section dédiée "Organigramme IA — Cartographie des agents" (7 étapes) dans le Help Panel admin. maxHeight bumped to 1500px pour accueillir les sections longues.
- [x] **2026-02-XX — Export PDF Organigramme IA** : nouvel utilitaire `/app/backend/utils/pdf_agents_org.py` + endpoint `GET /api/admin/agents/registry/pdf`. PDF premium 7 pages avec organigramme + annexe prompts intégraux. Bouton "Exporter en PDF" injecté dans `AdminAgentsOrg.jsx`.
- [x] **2026-02-XX — V1 Versioning/Audit IA** : système complet de traçabilité gouvernance IA pour audit CNIL/déontologique.
  - Nouvelle collection MongoDB `agents_versions` (snapshot complet : agents, prompts, red flags, base juridique, workflow config, hash SHA-256, changes_summary)
  - `utils/agents_snapshot.py` : capture state, hash dédup, diff humain
  - `routes/agents_versions.py` : POST snapshot manuel, GET liste paginée + recherche, GET détail, GET PDF audit
  - `utils/pdf_agents_audit.py` : rapport d'audit chronologique + annexe empreintes SHA-256
  - Hook auto-snapshot au démarrage du backend (idempotent — skip si hash identique)
  - Restauration "copy-only" : aucun write-back automatique pour préserver intégrité Git
  - Sous-onglets "Vue générale / Versions" dans `AdminAgentsOrg.jsx` + nouveau composant `AdminAgentsVersions.jsx` avec liste paginée, recherche, modal détail, copy config, export PDF audit
  - Tests : v1 auto-créée au boot, idempotence vérifiée (snapshot manuel sans changement → no_change), PDF audit valide, modal détail rendu OK
- [x] **TEST END-TO-END RÉEL EXÉCUTÉ** : sujet "Burn-out reconnu en accident du travail" généré du début à la fin
  - Plan IA généré en 19s (7 sections + 8 FAQ + 3 H1 options)
  - Brouillon généré en ~30s (parallel section generation, 14 red flags scannés)
  - Structure générée en 44s (11/11 clés, 5 blocages, 5 erreurs, 5 orientations, 5 FAQ)
  - 14 flags validés
  - Migration vers seed (+51 lignes)
  - Backend redémarré → auto-seed picked up new article → preview HTTP 200 ✅
  - Aperçu Web modal validé visuellement (10 sections rendues identiques à la page publiée)
  - Article de test ensuite nettoyé (DB + seed file) pour que l'utilisateur puisse re-tester sur un environnement vierge

## Calendrier SEO — Rappels Phases
### Phase 1 (FAIT) :
- [x] Optimisation `/calculatrice-ipp` : title/H1 "Calcul IPP", barème capital 2026 vérifié, 2 cas concrets, faute inexcusable, erreurs fréquentes, 5 FAQ Schema.org (~1100 mots)
- [x] Enrichissement `/guide/refus-mdph-aah-que-faire` (cas "renouvellement AAH refusé")
- [x] **2026-05-04** — Publication `/guide/refus-aah-rsdae-non-reconnue` (cible : refus RSDAE universel + longue-traîne motif 6). Maillage entrant ajouté depuis `refus-mdph-aah-que-faire`.

### Phase 2 (MI-MAI 2026 — dans 2-3 semaines) :
- [ ] Vérifier dans Search Console : impressions "calcul IPP", "simulateur rente IPP", "renouvellement aah refusé", "refus aah rsdae"
- [ ] Si les positions montent → passer à Phase 3
- [ ] Si stagnation → renforcer encore les pages existantes

### Phase 3 (JUIN 2026 — après validation Phase 2) :
- [ ] Créer `/guide/tableau-57-maladie-professionnelle` (guide complet, fort potentiel)

## Credentials Admin
- Admin: admin@accompagn-sante.fr / Admin2024!
- Backup Admin: backup@strategie-expertise-sante.fr / AdminSecours2026!
- Client test: demo@test.com / Password123!
