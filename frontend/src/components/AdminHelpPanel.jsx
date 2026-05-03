import { useState, useEffect, useRef, useMemo } from 'react';
import { HelpCircle, X, Search, ChevronRight, ArrowRight, Sparkles, BookOpen, Users, MessageSquare, Gift, Calendar, FolderOpen, Send, Zap, Brain, FileSearch, BarChart3, FileText, Star, Settings, Bell, PenTool, ChevronDown, RotateCcw } from 'lucide-react';

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
      { label: 'Statistiques', text: 'Vue d\'ensemble : codes actifs, utilisations totales, montant total des réductions.' },
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
      { label: 'Revue expert', text: 'Ajoutez votre analyse experte, recommandations et stratégie personnalisée.' },
      { label: 'Livraison', text: 'Générez le PDF final et envoyez-le au client. Le statut passe à "Livré".' },
    ],
    keywords: ['dossier express', 'payant', '97', 'analyse', 'pdf', 'livraison', 'expert', 'revue', 'document']
  },
  {
    id: 'analytics',
    tab: 'analytics',
    icon: BarChart3,
    title: 'Analytique',
    color: '#10b981',
    summary: 'Tableau de bord avec statistiques et graphiques de performance.',
    steps: [
      { label: 'Période', text: 'Sélectionnez la période d\'analyse : 7 jours, 30 jours, 90 jours.' },
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
      { label: 'Documents S3', text: 'Section "Documents stockés (S3)" : tous les fichiers uploadés via StrategiIA et Dossier Express, stockés durablement dans AWS S3.' },
      { label: 'Voir / Télécharger', text: 'Cliquez "Voir" pour ouvrir un document via une URL sécurisée temporaire (pre-signed URL, valide 1h). "Télécharger" pour le sauvegarder localement.' },
      { label: 'Tableau de bord S3', text: 'Graphiques d\'évolution : uploads par jour, volume total stocké (Mo/Go), répartition par source et type de fichier.' },
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
    summary: 'Retours stratégiques des clients : freins, besoins, compréhension de l\'offre.',
    steps: [
      { label: 'Lecture', text: 'Consultez tous les retours d\'expérience collectés après les analyses StrategiIA et Dossier Express.' },
      { label: 'Catégories', text: 'Les retours sont automatiquement catégorisés (juridique, médical, MDPH, assurantiel, accompagnement, etc.).' },
      { label: 'Filtrage', text: 'Filtrez par catégorie pour repérer les récurrences et les besoins non couverts.' },
      { label: 'Statistiques', text: 'Vue d\'ensemble : total retours, freins mentionnés, besoins exprimés, clarté de l\'offre.' },
    ],
    keywords: ['feedback', 'retour', 'expérience', 'frein', 'besoin', 'clarté', 'signal', 'client', 'avis stratégique']
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
      { label: 'Tutoriel Straté', text: 'Statistiques d\'engagement du tutoriel d\'onboarding : démarrages, taux de complétion et abandon par étape. Bouton "Relancer" pour revoir le tutoriel.' },
      { label: 'Préparation Production', text: 'Purgez les données de test (contacts, analyses, dossiers, avis, chatbot) et remettez les compteurs à zéro avant le lancement. Bouton "Purge complète" pour tout supprimer d\'un coup.' },
      { label: 'Notifications Push', text: 'Statut du Service Worker et des notifications push (VAPID).' },
      { label: 'IA V2 Readiness', text: 'Feu tricolore mesurant la progression vers l\'IA Prédictive V2. Score de 0 à 100 basé sur le volume de cas, la diversité, la complétude et la qualité. Minimum 500 cas exploitables pour le feu vert. Le graphique d\'évolution montre la progression dans le temps.' },
      { label: 'V2 Prédictive — Module dormant', text: 'Module préinstallé mais désactivé par défaut. Activation sécurisée (triple confirmation + saisie "ACTIVER V2") impossible sous 500 cas. Sandbox : testez l\'analyse V2 sur un texte libre sans impacter les clients. Comparateur : comparez une analyse V1 existante avec les signaux V2. Paramètres : ajustez les seuils (min cas, score requis, alertes max, prudence). Audit : journal complet de toutes les actions V2. Kill switch : désactivation instantanée vers V1 pur.' },
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
        style={{ maxHeight: isExpanded ? '500px' : '0', opacity: isExpanded ? 1 : 0 }}
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
