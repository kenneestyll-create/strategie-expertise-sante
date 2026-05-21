import { useState, useEffect, useRef, useMemo } from 'react';
import { HelpCircle, X, Search, ChevronRight, ArrowRight, Sparkles, BookOpen, Users, MessageSquare, Gift, Calendar, FolderOpen, Send, Zap, Brain, FileSearch, BarChart3, FileText, Star, Settings, Bell, PenTool, ChevronDown, RotateCcw, Mail, Crown, Lock, Video } from 'lucide-react';

const HELP_SECTIONS = [
  {
    id: 'contacts',
    tab: 'contacts',
    icon: Users,
    title: 'Contacts',
    color: '#6366f1',
    summary: 'Gérez toutes les demandes entrantes de vos prospects et clients.',
    steps: [
      { label: 'Consulter', text: 'Tous les formulaires de contact reçus apparaissent ici avec leur statut (Nouveau, En cours, Traité).' },
      { label: 'Filtrer', text: 'Utilisez les filtres par statut, canal (site, téléphone, email) et source pour cibler vos recherches.' },
      { label: 'Traiter', text: 'Cliquez sur un contact pour voir le détail, ajouter des notes internes et changer le statut.' },
      { label: 'Supprimer', text: 'Le bouton corbeille permet de supprimer définitivement un contact.' },
      { label: 'Tracking QR', text: 'En haut du tab, l\'indicateur "Contacts arrivés via QR" mesure les visiteurs venus depuis les QR codes des PDFs imprimés/partagés (Dossier Express IA, StratégiIA, Auto-diagnostic). Permet d\'identifier quel PDF circule le plus.' },
    ],
    keywords: ['contact', 'prospect', 'formulaire', 'demande', 'statut', 'nouveau', 'en cours', 'traité', 'filtre', 'notes', 'qr', 'qr code', 'tracking', 'pdf']
  },
  {
    id: 'avis',
    tab: 'avis',
    icon: MessageSquare,
    title: 'Avis',
    color: '#f59e0b',
    summary: 'Modérez et publiez les témoignages de vos clients.',
    steps: [
      { label: 'Modérer', text: 'Chaque avis soumis arrive en statut "En attente". Vous décidez de le publier ou le rejeter.' },
      { label: 'Publier', text: 'Les avis publiés apparaissent sur la page d\'accueil dans la section témoignages.' },
      { label: 'Modifier', text: 'Vous pouvez éditer le texte d\'un avis avant publication (anonymisation, corrections).' },
    ],
    keywords: ['avis', 'témoignage', 'modération', 'publier', 'rejeter', 'étoiles', 'note']
  },
  {
    id: 'referrals',
    tab: 'referrals',
    icon: Gift,
    title: 'Parrainage',
    color: '#ec4899',
    summary: 'Gérez les codes de parrainage et les réductions associées.',
    steps: [
      { label: 'Créer', text: 'Générez un code de parrainage unique pour un client existant.' },
      { label: 'Suivre', text: 'Consultez le nombre d\'utilisations de chaque code et les réductions accordées.' },
      { label: 'Statistiques', text: 'Vue d\'ensemble : codes actifs, utilisations totales, montant total des réductions.' },
    ],
    keywords: ['parrainage', 'code', 'réduction', 'remise', 'filleul', 'parrain', 'discount']
  },
  {
    id: 'bookings',
    tab: 'bookings',
    icon: Calendar,
    title: 'RDV',
    color: '#14b8a6',
    summary: 'Consultez et gérez les réservations d\'appels de vos clients.',
    steps: [
      { label: 'Consulter', text: 'Liste de tous les rendez-vous réservés via le site avec date, heure et coordonnées.' },
      { label: 'Statut', text: 'Suivez l\'état de chaque RDV (planifié, confirmé, effectué, annulé).' },
    ],
    keywords: ['rendez-vous', 'rdv', 'appel', 'réservation', 'calendrier', 'planifier']
  },
  {
    id: 'clients',
    tab: 'clients',
    icon: FolderOpen,
    title: 'Clients',
    color: '#8b5cf6',
    summary: 'Suivez vos clients convertis et leur historique.',
    steps: [
      { label: 'Liste', text: 'Tous les contacts convertis en clients apparaissent ici avec leur dossier.' },
      { label: 'Détail', text: 'Cliquez sur un client pour voir son historique complet, ses services et le montant facturé.' },
      { label: 'Conversion', text: 'Convertissez un contact en client depuis l\'onglet Contacts en renseignant le montant du service.' },
    ],
    keywords: ['client', 'converti', 'conversion', 'dossier', 'historique', 'montant', 'facture']
  },
  {
    id: 'relance',
    tab: 'relance',
    icon: Send,
    title: 'Relance',
    color: '#06b6d4',
    summary: 'Système de relance automatique pour les contacts sans réponse.',
    steps: [
      { label: 'Identifier', text: 'Les contacts inactifs depuis un certain temps sont listés ici pour relance.' },
      { label: 'Relancer', text: 'Envoyez un email de relance personnalisé en un clic.' },
      { label: 'Suivi', text: 'Le statut de chaque relance est tracé (envoyé, non envoyé).' },
    ],
    keywords: ['relance', 'suivi', 'email', 'rappel', 'inactif', 'automatique']
  },
  {
    id: 'alertes',
    tab: 'alertes',
    icon: Zap,
    title: 'Alertes',
    color: '#ef4444',
    summary: 'Alertes urgentes nécessitant votre attention immédiate.',
    steps: [
      { label: 'Priorité', text: 'Les alertes non traitées sont signalées par un badge rouge sur l\'onglet.' },
      { label: 'Types', text: 'Demandes urgentes, expertises imminentes, dossiers bloqués.' },
      { label: 'Traiter', text: 'Marquez une alerte comme traitée une fois l\'action effectuée.' },
    ],
    keywords: ['alerte', 'urgent', 'priorité', 'expertise', 'imminente', 'badge']
  },
  {
    id: 'strategiia',
    tab: 'strategiia',
    icon: Brain,
    title: 'StratégiIA',
    color: '#C9A84C',
    summary: 'Gérez les analyses stratégiques IA et les cas anonymisés.',
    steps: [
      { label: 'Analyses', text: 'Consultez toutes les analyses IA effectuées par les utilisateurs (gratuites et premium).' },
      { label: 'Premium', text: 'Les analyses premium en attente nécessitent votre validation avant envoi au client.' },
      { label: 'Cas anonymisés', text: 'Ajoutez des cas réels anonymisés pour enrichir la base de connaissances de l\'IA.' },
    ],
    keywords: ['stratégiia', 'analyse', 'ia', 'intelligence artificielle', 'premium', 'cas', 'anonymisé', 'validation']
  },
  {
    id: 'dossier-express',
    tab: 'dossier-express',
    icon: FileSearch,
    title: 'Dossier Express',
    color: '#d97706',
    summary: 'Traitez les dossiers express payants (97 EUR) — analyse complète sous 2h.',
    steps: [
      { label: 'Réception', text: 'Les dossiers payés arrivent avec le statut "En attente". Vous avez 2h pour les traiter.' },
      { label: 'Analyse', text: 'Consultez les documents soumis et l\'analyse IA pré-générée.' },
      { label: 'Documents uploadés — Télécharger les PDF originaux', text: 'Dans la modale du dossier, l\'onglet "Documents uploadés" liste tous les fichiers transmis par le client (PDF, JPG, scans, DOCX). Cliquez sur le bouton "Télécharger" à droite de chaque fichier pour récupérer l\'original via une URL sécurisée temporaire (pre-signed S3, valide 1h). Le bouton "Voir" ouvre une prévisualisation dans un nouvel onglet sans téléchargement.' },
      { label: 'Revue expert', text: 'Ajoutez votre analyse experte, recommandations et stratégie personnalisée.' },
      { label: 'Livraison', text: 'Générez le PDF final et envoyez-le au client. Le statut passe à "Livré".' },
    ],
    keywords: ['dossier express', 'payant', '97', 'analyse', 'pdf', 'livraison', 'expert', 'revue', 'document', 'télécharger', 'telecharger', 'download', 'documents uploadés', 'documents uploades', 'fichiers clients', 'original', 'pré-signed', 's3']
  },
  {
    id: 'kit-pro',
    tab: 'dossier-express',
    icon: Lock,
    title: '🔒 Kit Professionnel IA — Confidentiel admin',
    color: '#C9A84C',
    summary: 'Dossier de travail interne ultra-détaillé généré par IA pour chaque Dossier Express. Strictement réservé à l\'admin — ne jamais transmettre tel quel au client.',
    steps: [
      { label: 'Où le trouver ?', tab: 'dossier-express', text: 'Onglet "Dossier Express" → liste "Relecture expert". Cliquez "Consulter l\'analyse" (ou "Relire / Valider") sur n\'importe quelle ligne. Dans la modale qui s\'ouvre, 5 onglets en haut : Analyse | Documents uploadés | Prévisualisation PDF | Revue expert | 🔒 Kit Pro (dernier onglet, libellé doré avec cadenas).' },
      { label: 'À quoi ça sert', text: 'Le Kit Pro est votre "boîte à outils experte" pour préparer chaque dossier : stratégie, contestations, lettres prêtes à l\'emploi, calendrier de suivi. Il vous fait gagner 1 à 2h de travail par dossier en pré-mâchant l\'analyse juridique approfondie.' },
      { label: 'Les 7 sections générées', text: '1) Synthèse stratégique (vue d\'ensemble + chances de succès). 2) Diagnostic juridique (régime applicable, points forts/faibles). 3) Plan d\'action chronologique (étapes à suivre). 4) Lettres-types prêtes à personnaliser. 5) Arguments de contestation (taux IPP, refus, expertise). 6) Pièces à réclamer au client. 7) Calendrier de suivi (échéances à respecter).' },
      { label: 'Génération / Régénération', text: 'Si le kit n\'existe pas encore pour ce dossier, cliquez sur "Générer le kit" — l\'IA met 30 à 60 secondes pour produire les 7 sections. Si vous voulez le rafraîchir après mise à jour du dossier, cliquez "Régénérer". L\'ancien contenu est remplacé.' },
      { label: 'Notes admin internes', text: 'En bas du Kit Pro, une zone "Notes admin" vous permet de consigner vos observations privées (axes de plaidoirie, points de vigilance, contacts clés, etc.). Cliquez "Enregistrer les notes" pour sauvegarder. Ces notes ne sont JAMAIS visibles par le client — elles restent dans votre dossier de travail.' },
      { label: 'Export PDF', text: 'Bouton "Télécharger le PDF" en haut du Kit Pro → génère un PDF premium reprenant les 7 sections + vos notes admin. À utiliser uniquement pour vos archives ou un échange interne (avocat partenaire, médecin conseil). NE PAS envoyer au client.' },
      { label: 'Confidentialité stricte', text: 'Le Kit Pro contient des analyses brutes (taux d\'incertitude, stratégies de contestation, faiblesses identifiées) qui ne sont PAS destinées au client. Le client reçoit uniquement le PDF "Dossier Express IA" (analyse + revue expert), pas le Kit Pro. Cadenas doré = signal visuel "confidentiel".' },
      { label: 'Validation humaine obligatoire', text: 'Le Kit Pro est généré par IA (Claude Sonnet). Vous DEVEZ relire chaque section avant de l\'utiliser : l\'IA peut se tromper sur un détail juridique, un montant, une référence d\'article. Considérez le kit comme un "premier jet expert" — votre relecture humaine reste le filet de sécurité final.' },
      { label: 'Bonnes pratiques', text: 'Workflow recommandé : 1) Ouvrir le dossier → onglet Analyse pour le contexte. 2) Onglet Documents pour vérifier les pièces. 3) Onglet 🔒 Kit Pro → générer / lire les 7 sections. 4) Consigner vos notes admin. 5) Retour onglet "Revue expert" pour rédiger la version client définitive en s\'appuyant sur le kit.' },
    ],
    keywords: ['kit', 'kit pro', 'kit professionnel', 'kit-pro', 'confidentiel', 'admin', 'synthèse', 'stratégique', 'diagnostic juridique', 'plan d\'action', 'lettres-types', 'lettre type', 'contestation', 'arguments', 'pièces', 'calendrier', 'suivi', 'notes', 'admin_notes', 'régénérer', 'régénération', 'pdf', 'export', 'cadenas', 'lock', 'consulter l\'analyse', 'relire']
  },
  {
    id: 'analytics',
    tab: 'analytics',
    icon: BarChart3,
    title: 'Analytique',
    color: '#10b981',
    summary: 'Tableau de bord avec statistiques et graphiques de performance.',
    steps: [
      { label: 'Période', text: 'Sélectionnez la période d\'analyse : 7 jours, 30 jours, 90 jours.' },
      { label: 'Métriques', text: 'Visiteurs, contacts, conversions, revenus — tout est tracé.' },
      { label: 'Graphiques', text: 'Visualisez les tendances avec les courbes et diagrammes interactifs.' },
    ],
    keywords: ['analytique', 'statistiques', 'graphique', 'performance', 'visiteurs', 'conversion', 'revenus', 'tendance']
  },
  {
    id: 'documents',
    tab: 'documents',
    icon: FileText,
    title: 'Documents',
    color: '#0d9488',
    summary: 'Gérez les documents clients et consultez les fichiers stockés dans AWS S3.',
    steps: [
      { label: 'Documents clients', text: 'Tableau des documents uploadés par les clients via l\'espace client. Validez ou marquez comme illisibles.' },
      { label: 'Documents S3', text: 'Section "Documents stockés (S3)" : tous les fichiers uploadés via StrategiIA et Dossier Express, stockés durablement dans AWS S3.' },
      { label: 'Voir / Télécharger', text: 'Cliquez "Voir" pour ouvrir un document via une URL sécurisée temporaire (pre-signed URL, valide 1h). "Télécharger" pour le sauvegarder localement.' },
      { label: 'Tableau de bord S3', text: 'Graphiques d\'évolution : uploads par jour, volume total stocké (Mo/Go), répartition par source et type de fichier.' },
      { label: 'Actualiser', text: 'Le bouton "Actualiser" recharge les données S3 en temps réel.' },
    ],
    keywords: ['documents', 'faq', 'questions', 'ressources', 'guide', 'fichier', 's3', 'stockage', 'aws', 'upload', 'pre-signed', 'url', 'télécharger', 'voir']
  },
  {
    id: 'conseils-strate',
    tab: 'conseils-strate',
    icon: Star,
    title: 'Conseils Straté',
    color: '#C9A84C',
    summary: 'Gérez les conseils du jour affichés par la mascotte Straté.',
    steps: [
      { label: 'Ajouter', text: 'Créez un nouveau conseil avec texte, catégorie, dates de début/fin.' },
      { label: 'Planifier', text: 'Définissez la période d\'affichage de chaque conseil (dates de début et fin).' },
      { label: 'Priorité', text: 'Utilisez "Mettre en avant aujourd\'hui" pour forcer un conseil spécifique.' },
      { label: 'Prévisualiser', text: 'Le bouton Preview montre le conseil tel qu\'il apparaîtra dans la mascotte.' },
    ],
    keywords: ['conseil', 'straté', 'mascotte', 'astuce', 'tip', 'jour', 'planifier', 'priorité']
  },
  {
    id: 'feedback',
    tab: 'feedback',
    icon: MessageSquare,
    title: 'Retours d\'expérience',
    color: '#6366f1',
    summary: 'Retours stratégiques des clients : freins, besoins, compréhension de l\'offre.',
    steps: [
      { label: 'Lecture', text: 'Consultez tous les retours d\'expérience collectés après les analyses StrategiIA et Dossier Express.' },
      { label: 'Catégories', text: 'Les retours sont automatiquement catégorisés (juridique, médical, MDPH, assurantiel, accompagnement, etc.).' },
      { label: 'Filtrage', text: 'Filtrez par catégorie pour repérer les récurrences et les besoins non couverts.' },
      { label: 'Statistiques', text: 'Vue d\'ensemble : total retours, freins mentionnés, besoins exprimés, clarté de l\'offre.' },
    ],
    keywords: ['feedback', 'retour', 'expérience', 'frein', 'besoin', 'clarté', 'signal', 'client', 'avis stratégique']
  },
  {
    id: 'strate',
    tab: 'analytics',
    icon: Sparkles,
    title: 'Straté · Conciergerie IA',
    color: '#C9A84C',
    summary: 'Réceptionniste IA qui qualifie et oriente les visiteurs vers le bon parcours en 3 étapes max.',
    steps: [
      { label: 'Où le trouver ?', tab: 'analytics', text: 'Onglet "Analytique" → sous-onglet "Conciergerie Straté". Vous y voyez les KPI et le bouton kill switch.' },
      { label: 'Mission', text: 'Straté ne discute pas, il oriente. Sa seule mission : qualifier le visiteur en 2-3 clics et le router vers StratégiIA, Dossier Express, RDV, calculatrice ou guide.' },
      { label: 'Auto-ouverture', text: 'Straté s\'ouvre automatiquement après 15 sec d\'inactivité OU 40% de scroll. Limité à 1 fois / 24h via cookie. Jamais pendant la saisie d\'un formulaire.' },
      { label: 'Pages actives', text: 'Homepage, guides, tarifs, calculatrices, pages piliers (MDPH, AT/MP, expertise…). DÉSACTIVÉ sur StratégiIA, Dossier Express, Simulateur (tunnels actifs), admin et pages légales.' },
      { label: 'KPI principal', text: 'Le "Taux de routage" est LE chiffre à suivre. Objectif : 15-25% des sessions ouvertes finissent par un clic CTA. La répartition montre vers quoi ils cliquent (StratégiIA, RDV, guides…).' },
      { label: 'Kill switch', text: 'Bouton rouge "Désactiver Straté" en haut → effet immédiat, aucun déploiement. Utilisez-le si bug ou pour une période de test. Bouton vert pour réactiver.' },
      { label: 'Conformité RGPD', text: 'Bandeau visible à chaque ouverture rappelant de ne pas saisir de données médicales. Détection automatique des mots sensibles (cancer, métastase, NIR…) → redirection vers RDV humain. Logs anonymisés.' },
      { label: 'Bouton expert toujours visible', text: 'Lien "Besoin d\'un humain ? Parler à un expert" présent en permanence dans le header du chat. Le visiteur peut court-circuiter Straté à tout moment.' },
    ],
    keywords: ['strate', 'straté', 'conciergerie', 'réceptionniste', 'chatbot', 'orientation', 'routage', 'kill switch', 'kpi', 'conversion', 'taux', 'auto-ouverture', 'rgpd', 'expert', 'qualification']
  },
  {
    id: 'leads-seo',
    tab: 'analytics',
    icon: Mail,
    title: 'Leads SEO — Pages piliers',
    color: '#C9A84C',
    summary: 'Capture d\'emails sur les 5 pages stratégiques (MDPH, AT/MP, Expertise, Calc. IPP, Calc. AAH) via les blocs « Mémo gratuit ».',
    steps: [
      { label: 'Où le trouver ?', tab: 'analytics', text: 'Onglet "Analytique" → sous-onglet "Leads SEO". Vous y voyez total leads, taux d\'envoi email, leads des 7 derniers jours, répartition par page et la liste des 50 derniers leads.' },
      { label: 'Pourquoi c\'est important', text: 'Sans capture email, les visiteurs SEO disparaissent dans le néant. Avec ce système, chaque visiteur intéressé devient un contact qualifié auquel vous pouvez parler plus tard (forum, newsletter, suivi).' },
      { label: 'Comment ça marche', text: 'Sur chacune des 5 pages piliers, un bloc doré sobre propose un "Mémo gratuit" (contenu à forte valeur ajoutée, signé Équipe S.E.S). Le visiteur saisit son email + coche la case RGPD → reçoit immédiatement le mémo dans sa boîte.' },
      { label: 'Les 5 mémos disponibles', text: '1) MDPH — 5 erreurs qui font perdre 6 mois. 2) AT/MP — 7 réflexes immédiats. 3) Expertise — la phrase à NE JAMAIS dire. 4) IPP — calcul réel + marges de négociation. 5) AAH — décrypter le refus et préparer le RAPO.' },
      { label: 'Conformité RGPD', text: 'Consentement explicite (case à cocher obligatoire). Stockage du consent_date + IP partielle pour preuve. Désinscription mentionnée dans chaque email. Aucun email envoyé sans consentement.' },
      { label: 'Idempotence', text: 'Si le même visiteur s\'inscrit 2 fois sur la même page sous 7 jours, l\'email n\'est pas renvoyé en double (anti-spam). Au-delà de 7 jours, on suppose qu\'il a perdu le mémo et on le renvoie.' },
      { label: 'Stratégie', text: 'Objectif initial : 0 → 5-10 emails captés en 4-6 semaines. Avec ces premiers contacts, on pourra plus tard lancer le forum (recyclage Q&A) ou une newsletter mensuelle de stratégie.' },
    ],
    keywords: ['leads', 'seo', 'email', 'capture', 'mémo', 'memo', 'lead magnet', 'pilier', 'pillar', 'mdph', 'ipp', 'aah', 'expertise', 'newsletter', 'rgpd', 'consentement']
  },
  {
    id: 'editorial',
    tab: 'editorial',
    icon: Sparkles,
    title: 'Studio Éditorial — Production de guides SEO',
    color: '#C9A84C',
    summary: 'Architecture multi-agents (Planner → Writer → Critic juridique → Structurer) + 7 garde-fous + validation ciblée pour publier 1 guide SEO/semaine en toute fiabilité (95-98%).',
    steps: [
      { label: 'Où le trouver ?', tab: 'editorial', text: 'Onglet "Studio" dans la barre de navigation principale (à côté de Forum). Vous arrivez sur la page d\'accueil avec proposals, KPIs et liste des articles.' },
      { label: 'Choisir un sujet (3 options)', text: '1) Cliquez sur l\'un des 3 sujets proposés (re-tirables à volonté du pool de 30+). 2) Allez voir tout le pool. 3) Saisissez VOTRE propre sujet en bas. Les sujets choisis sont exclus du pool définitivement.' },
      { label: 'Étape 1 — Plan IA (Planner)', text: 'Cliquez "Générer le plan". L\'agent Planner produit en 5 sec : 3 variantes de H1, slug URL, méta-description, plan H2/H3 + 5-8 questions FAQ. Tout modifiable.' },
      { label: 'Étape 2 — Brouillon IA (Writer)', text: 'Cliquez "Générer le brouillon". L\'agent Writer rédige section par section en utilisant UNIQUEMENT la base de référence légale interne (~25 articles de loi, jurisprudences, chiffres pré-vérifiés). Tout ce qui sort de la base est marqué "[À VÉRIFIER]". Auto-retry des sections défaillantes.' },
      { label: 'Étape 3 — Critic juridique (NOUVEAU)', text: 'Onglet "Critic" → bouton "Auditer le brouillon". Un agent critique relit le brouillon ligne par ligne et identifie : hallucinations légales, chiffres non sourcés, jurisprudences inventées, conseils médicaux non couverts par la base. Retour structuré avec score de fiabilité + corrections suggérées. Vous pouvez réviser le brouillon en 1 clic ("Appliquer les corrections").' },
      { label: 'Étape 4 — Structurer pour publication', text: 'Onglet "Structurer" → bouton "Générer la structure publiable". L\'agent Structurer convertit le brouillon markdown en blocs structurés (réponse rapide, contexte, blocages, erreurs, stratégie, orientation, FAQ, maillage). Vous pouvez ensuite éditer chaque bloc librement dans des formulaires admin.' },
      { label: 'Étape 5 — Aperçu Web pixel-perfect', text: 'Bouton "Aperçu Web" en haut du brouillon : ouvre une modal qui rend l\'article EXACTEMENT comme il apparaîtra sur /guide/{slug} (mêmes Trust Badges, même typographie, même mise en page que les guides en production). Permet de valider visuellement avant publication.' },
      { label: 'Étape 6 — Validation ciblée', text: 'Onglet "À valider" : tableau de 5-15 drapeaux rouges à vérifier (lois, jurisprudences, chiffres, délais, termes médicaux, noms propres). Pour chacun : bouton "Vérifier" → ouvre Légifrance / service-public dans un nouvel onglet. Vous cochez "Validé" (vert) ou laissez en attente.' },
      { label: 'Étape 7 — Publication / Migration vers prod', text: 'Deux chemins après validation : 1) "Publier (preview)" → article visible immédiatement sur /guide/{slug} en environnement preview pour test final. 2) "Migrer vers production" → écrit l\'article dans le fichier seed_seo_pages.py. Au prochain redémarrage du backend (ou Save to GitHub + Deploy), l\'auto-seed pousse l\'article en production en ~30 secondes. Idempotent : ne touche jamais aux pages existantes.' },
      { label: 'Supprimer / Changer de sujet', text: 'Trois actions pour gérer vos brouillons : "Archiver" (suppression douce), "Supprimer" (suppression définitive), "Changer de sujet" (supprime + remet le sujet dans le pool). Toute suppression remet automatiquement le sujet dans le pool des 30 disponibles.' },
      { label: 'Saisir vos chiffres Search Console', text: 'Onglet "Perf" de chaque article : champs "Période / Impressions / Clics / Position moy.". Saisie mensuelle 30 sec. CTR calculé auto. Historique conservé.' },
      { label: 'Revalidation 6 mois', text: 'Tous les 6 mois après publication, alerte automatique sur la home du Studio : "X articles à revalider". Cliquez sur le titre → vérifiez que les chiffres et lois sont à jour → bouton "Toujours valable" OU mise à jour ciblée.' },
      { label: 'Modules avancés (mode veille)', text: 'Bouton "Paramètres" (haut droite du Studio) : 2 toggles désactivés par défaut : RAG live web (vérification temps réel Légifrance, ~10-30€/mois) et Génération dynamique sujets (IA propose selon SC, ~5-15€/mois). À activer plus tard quand le rythme est tenu.' },
      { label: 'Conformité juridique — 7 garde-fous', text: '1) prompts rigides (Planner / Writer / Critic / Structurer), 2) base de référence interne, 3) scanner red-flags automatique, 4) Critic juridique (NOUVEAU), 5) validation ciblée manuelle, 6) revalidation 6 mois, 7) disclaimer auto + Trust Badges. Aucune jurisprudence inventée, aucun chiffre fantaisiste, aucun nom propre, aucune donnée médicale sensible. Voir l\'onglet "Organigramme IA" pour visualiser tous les prompts.' },
      { label: 'Coût récurrent', text: '~3-5 €/mois en API IA (Claude Haiku 4.5 via Emergent LLM Key) pour 4 articles/mois — incluant les étapes Critic + Structuration. Aucun autre coût. Search Console = saisie manuelle = 0€.' },
    ],
    keywords: ['studio', 'éditorial', 'editorial', 'guide', 'seo', 'rédaction', 'ia', 'rédacteur', 'plan', 'brouillon', 'critic', 'critique', 'juridique', 'audit', 'red flag', 'drapeau', 'validation', 'légifrance', 'jurisprudence', 'loi', 'sujet', 'pool', 'revalidation', 'rag', 'haiku', 'claude', 'mémo', 'rgpd', 'cnil', 'fiabilité', 'garde-fou', 'structurer', 'aperçu', 'preview', 'migrer', 'seed', 'production', 'deploy', 'github', 'changer sujet', 'supprimer brouillon', 'planner', 'writer', 'agent', 'multi-agents', 'organigramme']
  },
  {
    id: 'video-factory',
    tab: 'video-factory',
    icon: Video,
    title: 'Video Factory V2 — Production vidéo IA + boucle apprentissage',
    color: '#C9A84C',
    summary: 'Studio interne autonome pour produire des packs vidéos courts (TikTok / Shorts / Reels) prêts à filmer + publier. 1 brief → 1 pack complet (hook, script, storyboard, .srt, SEO, CTA + UTM). Boucle V2 : saisissez vues / CTR / conversion après publication, les futures générations privilégient automatiquement les formats qui convertissent (floor exploration 10%).',
    steps: [
      { label: 'Où le trouver ?', tab: 'video-factory', text: 'Onglet "Video Factory" dans la barre de navigation admin (entre "Studio" et "Organigramme IA"). 3 sous-onglets : Générer / Historique / Performances.' },
      { label: 'Sous-onglet Générer — Remplir le brief', text: 'Topic libre (5-500 caractères) + Service cible (auto / 0€ / 29€ / 97€) + Intention (émotion / autorité / éducatif) + Urgence (faible / moyen / critique) + Plateforme (TikTok / YouTube Shorts / Facebook Reels / Instagram Reels) + Nb vidéos (1-5).' },
      { label: 'Mapping CTA automatique (règle dure)', text: 'Si service = auto → urgence critique = 97€ Dossier Express, urgence moyen = 29€ Analyse PDF, urgence faible = 0€ Diagnostic gratuit. Sinon, le service choisi est imposé. 1 SEUL CTA par vidéo, URL pré-mâchée avec UTM (?utm_source={plateforme}&utm_medium=short&utm_campaign={format}) pour traçabilité Analytics.' },
      { label: '7 formats verrouillés (F1-F7)', text: 'F1 Erreurs en expertise médicale · F2 Explications chiffrées (IPP, indemnisation) · F3 Cas réel anonymisé · F4 Analyse CPAM / médecin-conseil · F5 Réaction à un courrier administratif · F6 Erreurs de vocabulaire · F7 Checklist préparation dossier. L\'IA ne peut PAS inventer un nouveau format.' },
      { label: 'Forcer un format (optionnel)', text: 'Sélecteur "Forcer un format" en bas du form. Si vide = laissé à l\'IA OU choisi par la pondération si des poids existent (toggle "Utiliser les poids de performance"). Si renseigné = format imposé strictement.' },
      { label: 'Génération (~5-10s)', text: 'Cliquez "Générer le pack vidéo". Modèle utilisé : Claude Haiku 4.5 (1 seul appel LLM, cache activé). Coût ~0,006 €/vidéo. Si batch_size=5 → 5 vidéos en 1 appel, ~0,03 €.' },
      { label: 'Lecture du pack généré', text: 'Pour chaque vidéo : badges Format + Conversion ★/5 + Viral ★/5 (estimatif IA), Compliance OK ou À relire. 6 sections : Hooks (3 variantes A/B/C ≤12 mots) · Script (70-150 mots, parlé naturel) · Storyboard (6 plans max, type face-cam/broll/texte) · Sous-titres .srt (≤7-10 mots/segment, exportable) · Pack SEO (titre <60 car., description <200 car., 5-7 hashtags) · CTA unique avec URL UTM. Disclaimer pied de carte : "Contenu informatif, ne constitue pas un conseil…"' },
      { label: 'Actions par vidéo', text: 'Boutons par section : Copier (hooks/script/.srt/SEO/CTA), Télécharger .srt, Exporter JSON complet, Saisir métriques (ouvre modal V2), Marquer publié.' },
      { label: 'Workflow de production (en moins de 10 min)', text: '1) Lire le hook le plus fort des 3. 2) Lire le script — auto-éditer 1-2 mots si besoin. 3) Filmer face caméra (téléphone OK) en suivant le storyboard. 4) Importer dans CapCut / DaVinci. 5) Télécharger le .srt et le glisser dans l\'éditeur. 6) Ajouter B-roll Pexels avec les "broll_search_term" du storyboard. 7) Publier sur la plateforme cible. 8) Coller titre + description + hashtags depuis le pack SEO. 9) Coller le lien CTA en bio (URL avec UTM déjà prête).' },
      { label: 'Compliance automatique', text: 'Garde-fous backend : interdits "garanti / 100% / la CPAM ment / vous gagnerez X€" → audit regex objectif. Si fail → badge "À relire" et note précisant les patterns détectés. La pédagogie + "vous pourriez" + "dans certains cas" + cas anonymisés restent autorisés.' },
      { label: 'Sous-onglet Historique', text: 'Toutes vos générations passées (20 plus récentes), triées par date desc. Pour chaque run : nombre de vidéos, plateforme, urgence, statut (draft / published / archived), date. Boutons : Supprimer le run, et sur chaque vidéo Saisir métriques + Marquer publié.' },
      { label: 'Sous-onglet Performances (V2 — boucle d\'apprentissage)', text: 'Vue d\'ensemble des poids par format F1-F7 avec barres horizontales. Pour chaque format : moyennes views / CTR / conversion + nombre d\'échantillons. Tableau des 50 dernières métriques saisies. Bouton "Rafraîchir" pour reprendre les derniers calculs.' },
      { label: 'Saisir des métriques après publication', text: 'Depuis Historique → cliquez "Saisir métriques" sur une vidéo publiée → Modal demande : Vues totales, CTR (%), Taux de conversion (%), Note optionnelle. Au moment de l\'enregistrement, le backend recalcule automatiquement les poids par format (formule : 0.5×conversion + 0.3×CTR + 0.2×views, normalisée). Floor d\'exploration 10% par format garanti — aucun format n\'est jamais abandonné.' },
      { label: 'Cycle vertueux', text: 'Dès la 1re métrique saisie, les futures générations (avec toggle "Utiliser les poids" activé, par défaut) tirent un format au hasard pondéré par les poids. Plus vous saisissez de métriques, plus la machine privilégie les formats qui convertissent réellement. Vous gardez 10% d\'exploration pour découvrir de nouveaux gagnants.' },
      { label: 'Mode de choix transparent (V2 stabilisation)', text: 'Chaque génération affiche un badge mode coloré pour expliquer pourquoi tel format a été choisi : "Forcé manuellement" (violet) = vous l\'avez sélectionné · "Pondéré performance" (ambre) = backend a tiré pondéré selon vos métriques · "Fallback aléatoire" (gris) = pas de snapshot, tirage uniforme · "Libre IA" (bleu) = toggle désactivé, le LLM choisit. Garde anti-monoculture intégrée : si un format dépasse 65% d\'utilisation sur 7 jours glissants (min 5 runs), un reroll automatique l\'exclut une fois pour préserver la diversité. Dans l\'onglet Performances, un badge orange "🔥 Format dominant" apparaît sur les formats dont le poids dépasse 1,5× la moyenne — c\'est votre carte à jouer cette semaine.' },
      { label: 'V3 — Page SEO synchronisée (1 brief → vidéo + landing)', text: 'Toggle "Générer la page SEO synchronisée" dans le form Générer (+~0,005€/génération, total ~0,011€). Quand activé, après la vidéo, un 2e appel LLM produit une page web (markdown) STRICTEMENT dérivée du pack vidéo : intro reprenant le hook, blocs H2 développant le script, FAQ, méta-tags, slug kebab-case, mots-clés SEO, suggestions de liens internes, placeholder pour embed YouTube/TikTok. Le CTA SEO est COPIÉ VERBATIM de la vidéo (anti-divergence garantie côté backend, override Python — le LLM ne peut pas dévier). UTM différencié : ?utm_source=seo&utm_medium=organic&utm_campaign={format} (vs vidéo qui utilise utm_source=tiktok&utm_medium=short) — vous distinguez clairement les conversions organiques SEO vs vidéo dans Analytics. Affichage sous chaque génération dans une carte orange "📄 Page SEO synchronisée" avec : H1, méta-tags, intro, blocs H2 (5 max), FAQ (5 max), CTA en miroir, liens internes suggérés. Boutons : "Copier le markdown complet" (collez-le ensuite dans le Studio Éditorial existant pour relecture/publication finale), "Télécharger .md", "Copier JSON". Compliance unifiée : le badge racine "compliance_passed" est l\'ET logique de la vidéo ET de la page SEO — un fail sur l\'un = à relire. Activez ce toggle uniquement quand vous voulez vraiment publier les deux livrables ensemble (sinon laissez désactivé pour économiser).' },
      { label: 'Modèle & coûts', text: 'Claude Haiku 4.5 (Emergent LLM Key, prompt caching Anthropic). ~0,006 €/vidéo seule, ~0,011 €/vidéo+page SEO. 100 vidéos+SEO/mois = 1,10 €/mois total. Aucune API externe payante.' },
      { label: 'Limites et bonnes pratiques', text: '• Toujours relire le script en 10s avant tournage (la compliance est très solide mais l\'IA reste perfectible). • Filmer VOUS-MÊME pour conserver l\'authenticité founder (pas d\'avatar IA). • Saisir métriques 48-72h après publication (laisser le temps aux vues). • Ne pas mélanger plateformes (1 vidéo = 1 plateforme cible) pour bonne attribution UTM.' },
    ],
    keywords: ['video', 'vidéo', 'factory', 'tiktok', 'shorts', 'reels', 'instagram', 'youtube', 'facebook', 'hook', 'script', 'storyboard', 'srt', 'sous-titres', 'seo', 'cta', 'utm', 'haiku', 'claude', 'metrics', 'métriques', 'performance', 'poids', 'conversion', 'ctr', 'views', 'vues', 'pondération', 'exploration', 'floor', 'compliance', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'format', 'batch', 'disclaimer', 'historique', 'pack vidéo', 'production', 'editor', 'capcut']
  },
  {
    id: 'agents-org',
    tab: 'agents-org',
    icon: Crown,
    title: 'Organigramme IA — Cartographie des agents',
    color: '#C9A84C',
    summary: 'Carte visuelle de votre équipe d\'agents IA (PDG, Straté, StratégiIA, Dossier Express, Studio) avec leurs prompts système et garde-fous en lecture seule.',
    steps: [
      { label: 'Où le trouver ?', tab: 'agents-org', text: 'Onglet "Organigramme IA" dans la barre principale (à côté de "Studio"). Visualise la hiérarchie complète de vos agents IA en un coup d\'œil.' },
      { label: 'Pourquoi c\'est utile', text: 'Pour comprendre EXACTEMENT qui fait quoi dans votre écosystème IA, quels prompts sont en production, et quels garde-fous protègent vos visiteurs. Indispensable pour expliquer le fonctionnement à un partenaire, un investisseur, ou un audit RGPD/déontologique.' },
      { label: 'Hiérarchie en 3 niveaux', text: 'Niveau 0 : PDG Fondateur (vous — vision, validation finale). Niveau 1 : 3 agents en contact direct visiteur/client → Straté (Réceptionniste IA), StratégiIA (Analyse premium), Dossier Express (Pré-expertise documentaire). Niveau 2 : Équipe éditoriale du Studio SEO → Planner, Writer, Critic Juridique, Structurer.' },
      { label: 'Ouvrir le détail d\'un agent', text: 'Cliquez sur n\'importe quelle carte d\'agent → modal complet avec : Mission, Modèle utilisé (Claude Haiku/Sonnet), liste des garde-fous actifs, et le prompt système intégral (lecture seule). Bouton "Copier" pour le presse-papier.' },
      { label: 'Source du prompt', text: 'Chaque modal indique le fichier source exact (ex : routes/editorial.py → CRITIC_PROMPT) et le nom de la variable. Vous savez toujours où modifier un prompt si nécessaire (en passant par l\'agent dev Emergent).' },
      { label: 'Mise à jour automatique', text: 'L\'organigramme est piloté par /backend/routes/agents_registry.py. Chaque fois qu\'un nouvel agent est ajouté ou qu\'un prompt est modifié dans le code, l\'organigramme se met à jour automatiquement au prochain rechargement. Aucune maintenance manuelle.' },
      { label: 'Conformité & audit', text: 'Pratique pour répondre à une question type : "Quels prompts utilise votre IA pour rédiger des articles juridiques ?" → vous montrez l\'organigramme + le prompt du Critic juridique. Transparence totale, traçabilité complète.' },
    ],
    keywords: ['organigramme', 'agents', 'agent', 'ia', 'cartographie', 'hiérarchie', 'pdg', 'straté', 'strategiia', 'dossier express', 'planner', 'writer', 'critic', 'critique', 'structurer', 'prompt', 'système', 'garde-fou', 'lecture seule', 'audit', 'transparence', 'registre', 'registry']
  },
  {
    id: 'forum',
    tab: 'forum',
    icon: MessageSquare,
    title: 'Forum — Sujets graines',
    color: '#d97706',
    summary: 'Amorcez la communauté en publiant des sujets éditoriaux signés « Équipe S.E.S » sans passer par l\'inscription publique.',
    steps: [
      { label: 'Objectif', text: 'Le forum public démarre vide. Les sujets graines boostent le SEO longue traîne, renforcent votre E-E-A-T et incitent les visiteurs à poser leur première question.' },
      { label: 'Nettoyage pytest (si besoin)', text: 'Si votre forum en ligne affiche encore des posts de test ("Test pytest topic", "Report test"…), utilisez le bloc "Nettoyage chirurgical des données pytest" en haut du tab. 1) Cliquez "Analyser la base" → vous voyez exactement ce qui serait supprimé, avec aperçu. 2) Cliquez "Supprimer X entrées pytest" → tapez NETTOYER pour confirmer. Aucun vrai post n\'est touché (filtrage par motifs précis pseudos/emails/titres).' },
      { label: 'Publier', text: 'Choisissez une catégorie (AT/MP, MDPH, Expertise, Invalidité, Maladie Pro, Protection juridique), rédigez un titre accrocheur (≥ 10 caractères) et un contenu de qualité (≥ 80 caractères). Cliquez "Publier le sujet".' },
      { label: 'Signature', text: 'Par défaut, le sujet est signé « Équipe S.E.S » pour assurer la cohérence de marque. Vous pouvez personnaliser la signature au cas par cas (ex. : un intervenant spécifique).' },
      { label: 'Épinglage', text: 'Chaque sujet graine est épinglé par défaut → il apparaît en haut de sa catégorie. Vous pouvez désépingler ultérieurement via l\'icône pin/pin-off dans la liste.' },
      { label: 'Modérer', text: 'Les sujets graines sont listés sous le formulaire avec badges (épinglé, supprimé), date de publication, vues et nombre de réponses. 3 actions : épingler/désépingler, voir sur le forum (ouvre un nouvel onglet), supprimer.' },
      { label: 'Conformité', text: 'IMPORTANT : rédigez avec votre expertise réelle uniquement. Aucun faux témoignage, aucune personne identifiable, aucune statistique inventée (art. L.121-2 Code consommation + RGPD).' },
      { label: 'Idées de sujets', text: 'Exemples à fort potentiel : "Comment bien préparer son expertise médicale ?", "Refus MDPH : par où commencer ?", "Consolidation : que dire au médecin conseil ?", "Faute inexcusable : les 3 conditions". Posez une question ouverte en fin de contenu pour inviter aux réponses.' },
    ],
    keywords: ['forum', 'sujet', 'graine', 'seed', 'communauté', 'amorcer', 'publier', 'épingler', 'pin', 'éditorial', 'équipe ses', 'modération', 'entraide', 'discussion', 'topic', 'pytest', 'nettoyage', 'test', 'pollution', 'cleanup', 'discussions récentes']
  },
  {
    id: 'config',
    tab: 'config',
    icon: Settings,
    title: 'Configuration',
    color: '#6b7280',
    summary: 'Email, stockage, compteurs, chiffres clés, tarifs & promotions.',
    steps: [
      { label: 'Email (Resend)', text: 'Vérifiez le statut de la configuration email et envoyez un email test.' },
      { label: 'Stockage', text: 'Statut du stockage objet cloud pour les documents uploadés.' },
      { label: 'Compteur visiteurs (Hero)', text: 'Le compteur "X+ visiteurs" s\'incrémente automatiquement à chaque visite sur la page d\'accueil. Vous pouvez ajuster la valeur manuellement ici.' },
      { label: 'Base dossiers accompagnés', text: 'Ajustez la base du compteur "dossiers accompagnés à ce jour" affiché sur Dossier Express. Le total affiché = base + vrais dossiers enregistrés.' },
      { label: 'Le défi en chiffres', text: 'Éditez les 4 statistiques clés affichées sur la page d\'accueil (valeur, préfixe, unité, source). Cliquez "Enregistrer les chiffres" pour appliquer.' },
      { label: 'Tarifs & Promotions', text: 'Modifiez le prix de chaque prestation et ajoutez un badge promo (ex: "-20%", "Nouveau"). Les changements se reflètent sur la page Tarifs.' },
      { label: 'Tutoriel Straté', text: 'Statistiques d\'engagement du tutoriel d\'onboarding : démarrages, taux de complétion et abandon par étape. Bouton "Relancer" pour revoir le tutoriel.' },
      { label: 'Préparation Production', text: 'Purgez les données de test (contacts, analyses, dossiers, avis, chatbot) et remettez les compteurs à zéro avant le lancement. Bouton "Purge complète" pour tout supprimer d\'un coup.' },
      { label: 'Notifications Push', text: 'Statut du Service Worker et des notifications push (VAPID).' },
      { label: 'IA V2 Readiness', text: 'Feu tricolore mesurant la progression vers l\'IA Prédictive V2. Score de 0 à 100 basé sur le volume de cas, la diversité, la complétude et la qualité. Minimum 500 cas exploitables pour le feu vert. Le graphique d\'évolution montre la progression dans le temps.' },
      { label: 'V2 Prédictive — Module dormant', text: 'Module préinstallé mais désactivé par défaut. Activation sécurisée (triple confirmation + saisie "ACTIVER V2") impossible sous 500 cas. Sandbox : testez l\'analyse V2 sur un texte libre sans impacter les clients. Comparateur : comparez une analyse V1 existante avec les signaux V2. Paramètres : ajustez les seuils (min cas, score requis, alertes max, prudence). Audit : journal complet de toutes les actions V2. Kill switch : désactivation instantanée vers V1 pur.' },
    ],
    keywords: ['config', 'configuration', 'email', 'resend', 'stockage', 'compteur', 'hero', 'visiteurs', 'push', 'notification', 'tarifs', 'prix', 'promotion', 'badge', 'promo', 'chiffres', 'statistiques', 'défi', 'dossiers', 'hebdomadaire', 'semaine', 'base', 'tutoriel', 'onboarding', 'engagement', 'production', 'purge', 'nettoyage', 'supprimer', 'reset', 'v2', 'readiness', 'feu', 'tricolore', 'prédictive', 'score', 'dormant', 'sandbox', 'comparateur', 'kill switch', 'activation', 'audit']
  },
  {
    id: 'notifications',
    tab: 'notifications',
    icon: Bell,
    title: 'Notifications',
    color: '#f59e0b',
    summary: 'Gérez les notifications envoyées aux utilisateurs.',
    steps: [
      { label: 'Historique', text: 'Consultez toutes les notifications envoyées avec leur statut de livraison.' },
      { label: 'Envoyer', text: 'Envoyez des notifications push ou email à vos clients.' },
    ],
    keywords: ['notification', 'push', 'envoyer', 'alerte', 'message', 'email']
  },
  {
    id: 'templates',
    tab: 'templates',
    icon: PenTool,
    title: 'Templates',
    color: '#7c3aed',
    summary: 'Personnalisez les modèles d\'emails envoyés par la plateforme.',
    steps: [
      { label: 'Éditer', text: 'Modifiez le contenu HTML des emails automatiques (confirmation, relance, etc.).' },
      { label: 'Variables', text: 'Utilisez les variables dynamiques ({nom}, {email}, {date}) dans vos templates.' },
    ],
    keywords: ['template', 'modèle', 'email', 'html', 'personnaliser', 'variable']
  },
];

const HelpCard = ({ section, isExpanded, onToggle, onNavigate, index }) => {
  const Icon = section.icon;
  
  return (
    <div
      className="group rounded-xl border border-border/50 overflow-hidden transition-all duration-300"
      style={{
        animationDelay: `${index * 40}ms`,
        animation: 'helpCardIn 0.4s ease-out both',
        background: isExpanded ? `linear-gradient(135deg, ${section.color}08, transparent)` : undefined
      }}
      data-testid={`help-section-${section.id}`}
    >
      <button
        onClick={onToggle}
        className="w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-muted/50 transition-colors"
      >
        <div
          className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 transition-transform duration-300 group-hover:scale-110"
          style={{ backgroundColor: `${section.color}15`, color: section.color }}
        >
          <Icon className="w-4 h-4" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-foreground">{section.title}</p>
          <p className="text-[11px] text-muted-foreground truncate">{section.summary}</p>
        </div>
        <ChevronDown
          className="w-4 h-4 text-muted-foreground transition-transform duration-300 flex-shrink-0"
          style={{ transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)' }}
        />
      </button>
      
      <div
        className="overflow-hidden transition-all duration-400 ease-out"
        style={{ maxHeight: isExpanded ? '1500px' : '0', opacity: isExpanded ? 1 : 0 }}
      >
        <div className="px-4 pb-4 pt-1 space-y-2.5">
          {section.steps.map((step, i) => (
            <div key={i} className="flex gap-3 items-start" style={{ animationDelay: `${i * 60}ms` }}>
              <div className="flex-shrink-0 mt-0.5">
                <span
                  className="inline-flex items-center justify-center w-5 h-5 rounded-full text-[10px] font-bold text-white"
                  style={{ backgroundColor: section.color }}
                >
                  {i + 1}
                </span>
              </div>
              <div>
                <span className="text-xs font-semibold text-foreground">{step.label}</span>
                <p className="text-[11px] text-muted-foreground leading-relaxed">{step.text}</p>
              </div>
            </div>
          ))}
          
          <button
            onClick={() => onNavigate(section.tab)}
            className="mt-3 flex items-center gap-1.5 text-[11px] font-semibold px-3 py-1.5 rounded-lg transition-all hover:gap-2.5"
            style={{ color: section.color, backgroundColor: `${section.color}10` }}
            data-testid={`help-goto-${section.id}`}
          >
            Aller à cet onglet <ArrowRight className="w-3 h-3" />
          </button>
        </div>
      </div>
    </div>
  );
};

export const AdminHelpPanel = ({ onNavigateTab, onRestartTour }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');
  const [expandedId, setExpandedId] = useState(null);
  const searchRef = useRef(null);
  const panelRef = useRef(null);

  // Keyboard shortcut: Ctrl+H or ?
  useEffect(() => {
    const handler = (e) => {
      if ((e.ctrlKey && e.key === 'h') || (e.key === '?' && !['INPUT', 'TEXTAREA'].includes(e.target.tagName))) {
        e.preventDefault();
        setIsOpen(prev => !prev);
      }
      if (e.key === 'Escape' && isOpen) setIsOpen(false);
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [isOpen]);

  // Focus search on open
  useEffect(() => {
    if (isOpen) setTimeout(() => searchRef.current?.focus(), 300);
  }, [isOpen]);

  const filteredSections = useMemo(() => {
    if (!search.trim()) return HELP_SECTIONS;
    const q = search.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    return HELP_SECTIONS.filter(s => {
      const haystack = [s.title, s.summary, ...s.keywords, ...s.steps.map(st => st.label + ' ' + st.text)]
        .join(' ').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
      return haystack.includes(q);
    });
  }, [search]);

  const handleNavigate = (tab) => {
    setIsOpen(false);
    if (onNavigateTab) onNavigateTab(tab);
  };

  return (
    <>
      {/* Floating button */}
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 left-6 z-50 w-12 h-12 rounded-full flex items-center justify-center shadow-lg transition-all duration-300 hover:scale-110 hover:shadow-xl group"
        style={{
          background: 'linear-gradient(135deg, #C9A84C, #a08535)',
          color: '#fff',
        }}
        data-testid="admin-help-btn"
        title="Aide Admin (Ctrl+H)"
      >
        <HelpCircle className="w-5 h-5 transition-transform group-hover:rotate-12" />
        <span className="absolute -top-1 -right-1 w-4 h-4 bg-white rounded-full flex items-center justify-center">
          <Sparkles className="w-2.5 h-2.5 text-[#C9A84C]" />
        </span>
      </button>

      {/* Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-[60] bg-black/30 backdrop-blur-sm transition-opacity duration-300"
          onClick={() => setIsOpen(false)}
          data-testid="help-backdrop"
        />
      )}

      {/* Panel */}
      <div
        ref={panelRef}
        className="fixed top-0 right-0 z-[61] h-full w-full sm:w-[420px] bg-background border-l border-border shadow-2xl transition-transform duration-400 ease-out flex flex-col"
        style={{ transform: isOpen ? 'translateX(0)' : 'translateX(100%)' }}
        data-testid="admin-help-panel"
      >
        {/* Header */}
        <div className="flex-shrink-0 px-5 pt-5 pb-4 border-b border-border/60">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #C9A84C, #a08535)' }}>
                <BookOpen className="w-4.5 h-4.5 text-white" />
              </div>
              <div>
                <h2 className="text-base font-bold text-foreground">Guide Admin</h2>
                <p className="text-[10px] text-muted-foreground tracking-wide uppercase">S.E.S — Mode d'emploi</p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-muted transition-colors"
              data-testid="help-close-btn"
            >
              <X className="w-4 h-4 text-muted-foreground" />
            </button>
          </div>
          
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input
              ref={searchRef}
              type="text"
              placeholder="Rechercher une fonctionnalité..."
              value={search}
              onChange={(e) => { setSearch(e.target.value); setExpandedId(null); }}
              className="w-full pl-9 pr-4 py-2.5 text-sm rounded-xl border border-border/60 bg-muted/30 focus:outline-none focus:ring-2 focus:ring-[#C9A84C]/30 focus:border-[#C9A84C]/50 transition-all placeholder:text-muted-foreground/60"
              data-testid="help-search-input"
            />
            {search && (
              <button
                onClick={() => setSearch('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 rounded-full bg-muted flex items-center justify-center hover:bg-muted-foreground/20"
              >
                <X className="w-3 h-3 text-muted-foreground" />
              </button>
            )}
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto px-5 py-4 space-y-2.5 scrollbar-thin">
          {filteredSections.length > 0 ? (
            <>
              {search && (
                <p className="text-[11px] text-muted-foreground mb-2">
                  {filteredSections.length} résultat{filteredSections.length > 1 ? 's' : ''} pour « {search} »
                </p>
              )}
              {filteredSections.map((section, i) => (
                <HelpCard
                  key={section.id}
                  section={section}
                  index={i}
                  isExpanded={expandedId === section.id || (search.trim() !== '' && filteredSections.length === 1)}
                  onToggle={() => setExpandedId(expandedId === section.id ? null : section.id)}
                  onNavigate={handleNavigate}
                />
              ))}
            </>
          ) : (
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <Search className="w-10 h-10 text-muted-foreground/30 mb-3" />
              <p className="text-sm font-medium text-muted-foreground">Aucun résultat</p>
              <p className="text-xs text-muted-foreground/60 mt-1">Essayez un autre terme de recherche</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex-shrink-0 px-5 py-3 border-t border-border/60 bg-muted/20 space-y-2">
          {onRestartTour && (
            <button
              onClick={() => { setIsOpen(false); setTimeout(() => onRestartTour(), 400); }}
              className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-[11px] font-semibold transition-all border border-[#C9A84C]/30 hover:border-[#C9A84C]/60 hover:bg-[#C9A84C]/5"
              style={{ color: '#C9A84C' }}
              data-testid="help-restart-tour"
            >
              <RotateCcw className="w-3 h-3" />
              Revoir le tutoriel Straté
            </button>
          )}
          <p className="text-[10px] text-muted-foreground text-center">
            Raccourci clavier : <kbd className="px-1.5 py-0.5 rounded bg-muted text-[10px] font-mono border border-border/60">Ctrl + H</kbd> pour ouvrir/fermer
          </p>
        </div>
      </div>

      <style>{`
        @keyframes helpCardIn {
          from { opacity: 0; transform: translateY(8px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </>
  );
};
