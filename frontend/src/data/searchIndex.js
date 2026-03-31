import { MALADIES_PRO_TABLEAUX, TMS_LOCALISATION, IPP_EXEMPLES } from './maladiesProfessionnelles';
import { MDPH_DIRECTORY } from './mdphDirectory';

/*
  Each entry: { title, description, category, href, keywords[], anchor? }
  - category groups results visually
  - keywords are used for matching (lowercased at search time)
  - href is where the user navigates on click
  - anchor (optional) is an element id to scroll to on the target page
*/

/* ── Normalisation des accents ── */
function normalize(str) {
  return str.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
}

/* ── Dictionnaire de synonymes (français médical/juridique) ── */
const SYNONYMS = {
  'docteur': ['médecin', 'praticien', 'generaliste', 'spécialiste'],
  'médecin': ['docteur', 'praticien', 'generaliste', 'spécialiste'],
  'avocat': ['juriste', 'conseil juridique', 'defenseur', 'protection juridique'],
  'juriste': ['avocat', 'conseil juridique'],
  'indemnite': ['indemnisation', 'compensation', 'reparation', 'dedommagement', 'argent', 'somme'],
  'indemnisation': ['indemnite', 'compensation', 'reparation', 'dedommagement', 'argent'],
  'argent': ['indemnisation', 'indemnite', 'paiement', 'somme', 'montant'],
  'rente': ['indemnisation', 'pension', 'capital', 'revenu'],
  'pension': ['rente', 'indemnisation', 'allocation', 'revenu'],
  'salaire': ['revenu', 'rémunération', 'gains', 'traitement', 'paie'],
  'revenu': ['salaire', 'gains', 'rémunération'],
  'handicap': ['invalidité', 'incapacité', 'deficience', 'inaptitude', 'séquelles'],
  'invalidité': ['handicap', 'incapacité', 'inaptitude'],
  'incapacité': ['handicap', 'invalidité', 'ipp', 'taux', 'séquelles'],
  'séquelles': ['incapacité', 'handicap', 'consequences', 'invalidité', 'blessure'],
  'blessure': ['lesion', 'séquelles', 'traumatisme', 'dommage'],
  'lesion': ['blessure', 'atteinte', 'dommage'],
  'accident': ['sinistre', 'at', 'incident', 'dommage'],
  'maladie': ['pathologie', 'affection', 'trouble', 'mp'],
  'pathologie': ['maladie', 'affection', 'trouble'],
  'cpam': ['sécurité sociale', 'secu', 'caisse', 'assurance maladie'],
  'sécurité sociale': ['cpam', 'secu', 'caisse'],
  'secu': ['cpam', 'sécurité sociale', 'caisse'],
  'tribunal': ['justice', 'juge', 'audience', 'contentieux', 'recours'],
  'recours': ['contestation', 'appel', 'tribunal', 'litige'],
  'contestation': ['recours', 'refus', 'appel', 'opposition'],
  'refus': ['rejet', 'contestation', 'recours'],
  'emploi': ['travail', 'poste', 'profession', 'metier', 'job'],
  'travail': ['emploi', 'poste', 'profession', 'metier', 'activité'],
  'licenciement': ['rupture', 'renvoi', 'fin de contrat', 'inaptitude'],
  'inaptitude': ['licenciement', 'reclassement', 'incapacité'],
  'reclassement': ['reconversion', 'mutation', 'changement de poste'],
  'reconversion': ['reclassement', 'formation', 'changement de metier'],
  'dossier': ['document', 'formulaire', 'pieces', 'justificatif'],
  'document': ['dossier', 'formulaire', 'pieces', 'papiers', 'justificatif'],
  'formulaire': ['cerfa', 'document', 'imprime'],
  'cerfa': ['formulaire', 'document', 'imprime'],
  'expert': ['expertise', 'médecin expert', 'évaluation'],
  'expertise': ['expert', 'évaluation', 'examen'],
  'aide': ['allocation', 'prestation', 'soutien', 'accompagnement'],
  'allocation': ['aide', 'prestation', 'aah', 'pension'],
  'prix': ['tarif', 'cout', 'montant', 'formule'],
  'tarif': ['prix', 'cout', 'montant', 'formule'],
  'cout': ['prix', 'tarif', 'montant'],
  'rdv': ['rendez-vous', 'agenda', 'consultation', 'creneau'],
  'rendez-vous': ['rdv', 'agenda', 'consultation', 'creneau', 'booking'],
  'consultation': ['rendez-vous', 'rdv', 'visite'],
  'scanner': ['scan', 'numeriser', 'photo', 'document', 'appareil photo'],
  'scan': ['scanner', 'numeriser', 'photo'],
  'ia': ['intelligence artificielle', 'strategiia', 'analyse automatique'],
  'strategiia': ['ia', 'simulateur', 'analyse', 'intelligence artificielle'],
  'pj': ['protection juridique', 'assurance', 'avocat'],
  'dos': ['douleur', 'rachis', 'lombalgie', 'hernie', 'sciatique', 'lumbago'],
  'lombalgie': ['dos', 'rachis', 'lumbago', 'douleur'],
  'hernie': ['disque', 'dos', 'rachis', 'sciatique'],
  'epaule': ['coiffe', 'rotateurs', 'tendinite', 'tms'],
  'canal carpien': ['poignet', 'main', 'tms', 'syndrome', 'nerf median'],
  'poignet': ['canal carpien', 'main', 'tms'],
  'genou': ['menisque', 'hygroma', 'rotule', 'tms'],
  'amiante': ['mesotheliome', 'plaque pleurale', 'cancer', 'poumon', 'tableau 30'],
  'burn out': ['burnout', 'epuisement', 'depression', 'stress', 'souffrance'],
  'burnout': ['burn out', 'epuisement', 'depression', 'stress'],
  'depression': ['burn out', 'burnout', 'souffrance', 'psychologique'],
  'stress': ['burn out', 'burnout', 'souffrance', 'harcelement'],
  'harcelement': ['moral', 'stress', 'souffrance', 'discrimination'],
  'parrainage': ['parrain', 'filleul', 'reduction', 'avantage', 'recommandation'],
};

function getSynonyms(term) {
  const normalized = normalize(term);
  return SYNONYMS[normalized] || [];
}

const PAGES = [
  { title: "Accueil", description: "Page d'accueil de Stratégie & Expertise Santé", category: "Pages", href: "/", keywords: ["accueil", "home", "bienvenue", "presentation", "decouvrir"] },
  { title: "A propos — Mon parcours", description: "Decouvrez l'expérience et le parcours professionnel", category: "Pages", href: "/a-propos", keywords: ["parcours", "experience", "a propos", "qui", "biographie", "profil", "formation", "competences", "équipe"] },
  { title: "Accompagnements", description: "Nos services d'accompagnement personnalisé pour AT/MP, MDPH, expertise", category: "Pages", href: "/accompagnements", keywords: ["accompagnement", "service", "aide", "soutien", "conseil", "prestation", "offre", "suivi", "prise en charge"] },
  { title: "Expertise médicale", description: "Comprendre et se preparer a l'expertise médicale, médecin expert, évaluation", category: "Pages", href: "/expertise-medicale", keywords: ["expertise", "médicale", "médecin", "conseil", "évaluation", "expert", "examen", "préparation", "rapport", "docteur", "avis", "contre-expertise"] },
  { title: "Accident du travail / Maladie professionnelle", description: "Vos droits en cas d'AT/MP — declaration, reconnaissance, indemnisation", category: "Pages", href: "/accident-travail-maladie-professionnelle", keywords: ["accident", "travail", "maladie", "professionnelle", "at", "mp", "cpam", "declaration", "reconnaissance", "sinistre", "blessure", "indemnisat", "droit", "employeur", "sécurité sociale"] },
  { title: "MDPH", description: "Tout savoir sur la Maison Departementale des Personnes Handicapees — droits, AAH, RQTH", category: "Pages", href: "/mdph", keywords: ["mdph", "handicap", "maison departementale", "droits", "aah", "rqth", "carte", "invalidité", "pch", "orientation", "taux", "incapacité", "reconnaissance", "dossier"] },
  { title: "Protection juridique", description: "Activer et utiliser votre protection juridique — avocat, recours, assurance", category: "Pages", href: "/protection-juridique", keywords: ["protection", "juridique", "assurance", "avocat", "recours", "defense", "pj", "litige", "tribunal", "justice", "contrat", "garantie", "sinistre"] },
  { title: "Seminaires", description: "Nos seminaires de formation et d'information santé/droit", category: "Pages", href: "/seminaires", keywords: ["seminaire", "formation", "conference", "atelier", "événement", "webinaire", "inscription", "programme"] },
  { title: "Entreprises", description: "Offres pour les entreprises, CSE, employeurs — prevention, formation", category: "Pages", href: "/entreprises", keywords: ["entreprise", "cse", "employeur", "salarie", "prevention", "formation", "collectif", "groupe", "comite", "social", "economique"] },
  { title: "Partenaires", description: "Nos partenaires de confiance — réseau professionnel", category: "Pages", href: "/partenaires", keywords: ["partenaire", "réseau", "collaboration", "professionnel", "association"] },
  { title: "Forum", description: "Communaute d'entraide — posez vos questions, partagez votre experience", category: "Pages", href: "/forum", keywords: ["forum", "communauté", "discussion", "entraide", "question", "réponse", "témoignage", "partage", "echange"] },
  { title: "Avis clients", description: "Témoignages et avis de nos clients satisfaits", category: "Pages", href: "/avis", keywords: ["avis", "témoignage", "client", "satisfaction", "note", "retour", "experience", "recommandation", "etoile"] },
  { title: "Ressources", description: "Base de connaissances, guides pratiques, FAQ et encyclopedie", category: "Pages", href: "/ressources", keywords: ["ressource", "guide", "faq", "information", "documentation", "encyclopedie", "connaissance", "base", "bibliotheque", "savoir"] },
  { title: "Contact", description: "Nous contacter pour une question ou un rendez-vous", category: "Pages", href: "/contact", keywords: ["contact", "email", "téléphone", "message", "joindre", "ecrire", "appeler", "formulaire", "demande"] },
  { title: "Tarifs", description: "Nos tarifs et formules d'accompagnement — prix et options", category: "Pages", href: "/tarifs", keywords: ["tarif", "prix", "formule", "paiement", "cout", "pass", "abonnement", "offre", "montant", "euro", "budget"] },
  { title: "Prendre rendez-vous", description: "Reserver un creneau en ligne — agenda de consultation", category: "Pages", href: "/agenda", keywords: ["rendez-vous", "agenda", "reserver", "calendrier", "creneau", "booking", "rdv", "consultation", "disponibilite", "horaire"] },
  { title: "Espace client", description: "Acceder a votre espace personnel securise — suivi de dossier", category: "Pages", href: "/espace-client", keywords: ["espace client", "connexion", "dossier", "suivi", "portail", "compte", "personnel", "login", "mot de passe"] },
  { title: "Simulateur de droits", description: "Simulez vos droits en quelques questions — éligibilite AT/MP/MDPH", category: "Pages", href: "/simulateur", keywords: ["simulateur", "droits", "éligibilite", "test", "questionnaire", "verification", "strategiia", "ia", "analyse", "diagnostic"] },
  { title: "Mentions légales", description: "Informations légales du site", category: "Pages", href: "/mentions-legales", keywords: ["mentions", "légales", "rgpd", "données", "editeur", "hebergeur", "responsabilite"] },
  { title: "Dossier Express IA", description: "Analyse complete de votre dossier par IA avec rapport PDF sous 2h — 97 euros", category: "Pages", href: "/dossier-express", keywords: ["dossier", "express", "analyse", "rapport", "pdf", "ia", "strategiia", "97", "rapide", "intelligence artificielle", "automatique", "premium"] },
  { title: "CGU", description: "Conditions générales d'utilisation du site et des services", category: "Pages", href: "/cgu", keywords: ["cgu", "conditions", "générales", "utilisation", "reglement", "contrat", "acceptation", "service"] },
  { title: "Politique de confidentialité", description: "Protection de vos données personnelles (RGPD)", category: "Pages", href: "/politique-confidentialite", keywords: ["rgpd", "confidentialité", "données", "protection", "vie privee", "consentement", "cookie", "personnel"] },
  { title: "Le defi en chiffres", description: "Statistiques nationales : accidents du travail, maladies professionnelles, handicap", category: "Pages", href: "/", anchor: "chiffres", keywords: ["chiffres", "statistiques", "700000", "accidents", "12 millions", "handicap", "mdph", "50000", "maladies", "données", "nombres"] },
  { title: "Parrainage", description: "Programme de parrainage — parrainez un proche et bénéficiez d'avantages", category: "Pages", href: "/parrainage", keywords: ["parrainage", "parrain", "filleul", "reduction", "avantage", "recommandation", "offre", "partage", "invitation", "code"] },
  // Anchored sections
  { title: "Liste des accompagnements", description: "Tous nos services : AT/MP, MDPH, expertise médicale, protection juridique", category: "Sections", href: "/accompagnements", anchor: "services-liste", keywords: ["liste", "services", "accompagnement", "at", "mp", "mdph", "expertise", "catalogue"] },
  { title: "Regimes speciaux (SNCF, RATP)", description: "Accompagnement dedie aux agents des regimes speciaux", category: "Sections", href: "/accompagnements", anchor: "regimes-speciaux", keywords: ["regimes", "speciaux", "sncf", "ratp", "cheminots", "agents", "fonctionnaire", "public"] },
  { title: "Tarif StrategiIA", description: "Analyse IA gratuite avec options premium des 29 euros", category: "Sections", href: "/tarifs", anchor: "tarif-strategiia", keywords: ["tarif", "prix", "strategiia", "analyse", "ia", "29", "gratuit", "premium", "formule"] },
  { title: "Tarif Dossier Express IA", description: "Analyse complete par IA + rapport PDF — 97 euros", category: "Sections", href: "/tarifs", anchor: "tarif-dossier-express", keywords: ["tarif", "prix", "dossier", "express", "97", "rapport", "pdf", "premium"] },
  { title: "Glossaire santé & droit", description: "Lexique des termes clés : AT, MP, IPP, IP, PGPF, MDPH, AAH, RQTH", category: "Sections", href: "/ressources", anchor: "glossaire", keywords: ["glossaire", "lexique", "definition", "at", "mp", "ipp", "aah", "rqth", "vocabulaire", "ip", "pgpf", "incidence professionnelle", "perte de gains futurs", "terme", "signification", "acronyme"] },
  { title: "Encyclopedie des maladies professionnelles", description: "Tableaux, TMS, IPP, IP, PGPF et pathologies hors tableau", category: "Sections", href: "/ressources", anchor: "encyclopedie", keywords: ["encyclopedie", "tableaux", "tms", "ipp", "pathologie", "maladie", "incidence professionnelle", "ip", "pgpf", "perte de gains futurs", "liste", "référénce"] },
  { title: "FAQ — Questions frequentes", description: "Réponses aux questions les plus posees", category: "Sections", href: "/ressources", anchor: "faq", keywords: ["faq", "questions", "frequentes", "réponses", "aide", "comment", "pourquoi", "quand", "combien"] },
  { title: "Guides pratiques", description: "Par ou commencer ? Guides étape par étape", category: "Sections", href: "/ressources", anchor: "guides", keywords: ["guide", "pratique", "etape", "demarche", "commencer", "procedure", "comment faire", "méthode"] },
  { title: "Bibliotheque de documents", description: "Formulaires, modeles de lettres et documents utiles", category: "Sections", href: "/ressources", anchor: "bibliotheque", keywords: ["bibliotheque", "document", "formulaire", "lettre", "modele", "telechargement", "cerfa", "courrier", "template", "pdf"] },
];

const IP_PGPF = [
  { title: "Incidence Professionnelle (IP)", description: "Indemnisation des conséquences sur la carrière : pénibilité accrue, dévalorisation, reconversion", category: "Indemnisation", href: "/ressources", anchor: "encyclopedie", keywords: ["incidence professionnelle", "ip", "pénibilité", "devalorisation", "reconversion", "carrière", "indemnisation", "prejudice", "emploi", "consequence", "impact", "travail", "profession"] },
  { title: "Perte de Gains Professionnels Futurs (PGPF)", description: "Compensation de la perte définitive de revenus après consolidation — capitalisation", category: "Indemnisation", href: "/ressources", anchor: "encyclopedie", keywords: ["pgpf", "perte de gains futurs", "perte de gains professionnels futurs", "capitalisation", "revenus", "bareme", "gazette du palais", "rente", "salaire", "consolidation", "projection", "manque a gagner"] },
  { title: "Critères IP — Pénibilité accrue", description: "Conditions de travail plus pénibles dues aux séquelles : efforts supplémentaires, douleurs", category: "Indemnisation", href: "/ressources", anchor: "encyclopedie", keywords: ["pénibilité", "accrue", "efforts", "douleur", "fatigue", "séquelles", "travail", "ip", "conditions", "souffrance"] },
  { title: "Critères IP — Dévalorisation professionnelle", description: "Réduction de l'employabilité suite au handicap : discrimination, postes limités", category: "Indemnisation", href: "/ressources", anchor: "encyclopedie", keywords: ["devalorisation", "employabilite", "handicap", "discrimination", "embauche", "marche du travail", "ip", "chomage", "difficulté"] },
  { title: "Calcul PGPF — Méthode de capitalisation", description: "Projection de carrière, évolution salariale, impact du handicap, barème de capitalisation", category: "Indemnisation", href: "/ressources", anchor: "encyclopedie", keywords: ["calcul", "pgpf", "capitalisation", "projection", "carrière", "salaire", "bareme", "euro de rente", "méthode", "montant", "estimation"] },
  { title: "PGPA vs PGPF — Distinction", description: "Perte de gains actuels (avant consolidation) vs perte de gains futurs (apres consolidation)", category: "Indemnisation", href: "/ressources", anchor: "encyclopedie", keywords: ["pgpa", "pgpf", "distinction", "consolidation", "arret", "indemnites journalieres", "perte de revenus", "différence", "avant", "apres"] },
];

const TOOLS = [
  { title: "Calculatrice IPP", description: "Estimez votre indemnisation selon votre taux d'incapacité permanente partielle — avec IP et PGPF", category: "Outils", href: "/calculatrice-ipp", keywords: ["calculatrice", "ipp", "incapacité", "permanente", "partielle", "indemnisation", "rente", "capital", "taux", "calcul", "estimation", "séquelles", "incidence professionnelle", "ip", "pgpf", "perte de gains futurs", "montant", "combien", "simuler"] },
  { title: "Calculatrice AAH", description: "Estimez le montant de votre Allocation aux Adultes Handicapes", category: "Outils", href: "/calculatrice-aah", keywords: ["calculatrice", "aah", "allocation", "adulte", "handicape", "montant", "calcul", "estimation", "invalidité", "revenu", "aide", "simuler", "combien"] },
  { title: "Simulateur de droits — StrategiIA", description: "Verifiez votre éligibilite aux différéntes aides et dispositifs grace a l'IA", category: "Outils", href: "/simulateur", keywords: ["simulateur", "droits", "éligibilite", "aide", "dispositif", "strategiia", "ia", "intelligence artificielle", "analyse", "diagnostic", "test", "gratuit"] },
  { title: "Dossier Express IA", description: "Analyse complete par intelligence artificielle avec rapport PDF", category: "Outils", href: "/dossier-express", keywords: ["dossier", "express", "ia", "rapport", "pdf", "analyse", "intelligence artificielle", "premium", "97", "rapide", "complet"] },
  { title: "Scanner de documents", description: "Numerisez vos documents médicaux avec l'appareil photo de votre téléphone", category: "Outils", href: "/espace-client", keywords: ["scanner", "scan", "document", "photo", "numeriser", "appareil photo", "téléphone", "camera", "piece", "justificatif", "medical"] },
];

const MALADIES = MALADIES_PRO_TABLEAUX.map(m => ({
  title: `Tableau ${m.numero} — ${m.titre}`,
  description: `Delai : ${m.delai} | ${m.travaux}`,
  category: "Maladies professionnelles",
  href: "/ressources#encyclopedie",
  keywords: [
    m.numero, normalize(m.titre), normalize(m.travaux), normalize(m.delai),
    "tableau", "maladie", "professionnelle"
  ].join(' ').split(/[\s,()]+/).filter(Boolean)
}));

const TMS = TMS_LOCALISATION.map(t => ({
  title: `TMS ${t.tableau} — ${t.zone}`,
  description: t.pathologies.join(', '),
  category: "Maladies professionnelles",
  href: "/ressources#encyclopedie",
  keywords: [
    normalize(t.tableau), normalize(t.zone),
    ...t.pathologies.map(p => normalize(p)),
    "tms", "trouble", "musculo", "squelettique", "tableau 57", "douleur", "tendinite"
  ]
}));

const IPP_ITEMS = IPP_EXEMPLES.map(ex => ({
  title: `IPP ${ex.taux}% — ${ex.description}`,
  description: ex.indemnisation,
  category: "IPP — Exemples",
  href: "/ressources#encyclopedie",
  keywords: [
    `${ex.taux}%`, normalize(ex.description), normalize(ex.indemnisation),
    "ipp", "incapacité", "taux", "indemnisation", "exemple", "montant"
  ]
}));

const MDPH_ITEMS = MDPH_DIRECTORY.map(m => ({
  title: `MDPH ${m.nom} (${m.dep})`,
  description: m.adresse,
  category: "Annuaire MDPH",
  href: "/ressources#encyclopedie",
  keywords: [normalize(m.dep), normalize(m.nom), "mdph", "maison", "departement", "handicap", "adresse", "annuaire"]
}));

const AIDES = [
  { title: "CMI Invalidité", description: "Carte Mobilite Inclusion mention invalidité — taux supérieur ou égal a 80%", category: "Aides MDPH", href: "/ressources#encyclopedie", keywords: ["cmi", "carte", "mobilite", "inclusion", "invalidité", "80", "handicap", "demi-part", "fiscal", "priorité"] },
  { title: "CMI Priorite", description: "Carte Mobilite Inclusion mention priorité — station debout penible", category: "Aides MDPH", href: "/ressources#encyclopedie", keywords: ["cmi", "carte", "mobilite", "priorité", "station debout", "file d'attente", "place", "transport"] },
  { title: "CMI Stationnement", description: "Carte Mobilite Inclusion mention stationnement — perimetre de marche limite", category: "Aides MDPH", href: "/ressources#encyclopedie", keywords: ["cmi", "carte", "stationnement", "parking", "place handicape", "voiture", "vehicule", "gic"] },
  { title: "PCH — Aide humaine", description: "Financement d'un aidant pour les actes essentiels", category: "Aides MDPH", href: "/ressources#encyclopedie", keywords: ["pch", "aide", "humaine", "aidant", "toilette", "habillage", "alimentation", "prestation compensation", "domicile", "quotidien"] },
  { title: "PCH — Aides techniques", description: "Fauteuil roulant, protheses, materiel adapte", category: "Aides MDPH", href: "/ressources#encyclopedie", keywords: ["pch", "aide", "technique", "fauteuil", "prothese", "materiel", "équipement", "appareillage", "adaptation"] },
  { title: "PCH — Amenagement du logement", description: "Rampe, douche italienne, monte-escalier, domotique", category: "Aides MDPH", href: "/ressources#encyclopedie", keywords: ["pch", "logement", "aménagément", "rampe", "douche", "monte-escalier", "accessibilite", "domicile", "travaux", "maison", "appartement"] },
  { title: "PCH — Amenagement du vehicule", description: "Adaptation du vehicule et surcouts de transport", category: "Aides MDPH", href: "/ressources#encyclopedie", keywords: ["pch", "vehicule", "voiture", "transport", "conduite", "adaptation", "permis", "deplacement"] },
  { title: "AAH — Allocation Adultes Handicapes", description: "Aide financière mensuelle (max 971,37 euros) pour personnes handicapees", category: "Aides MDPH", href: "/calculatrice-aah", keywords: ["aah", "allocation", "adulte", "handicape", "aide", "financière", "revenu", "mensuel", "montant", "argent", "prestation", "971"] },
  { title: "RQTH — Travailleur Handicape", description: "Reconnaissance ouvrant des droits en emploi — aménagément de poste, Agefiph", category: "Aides MDPH", href: "/mdph", keywords: ["rqth", "travailleur", "handicape", "emploi", "aménagément", "poste", "embauche", "agefiph", "reconnaissance", "droit", "obligation", "quota"] },
  { title: "Reconnaissance hors tableau", description: "Procedure de reconnaissance via le CRRMP (Alinea 3 et 4)", category: "Maladies professionnelles", href: "/ressources#encyclopedie", keywords: ["hors tableau", "crrmp", "alinea", "reconnaissance", "comite", "regional", "maladie", "professionnelle", "procedure", "complémentaire"] },
];

const GUIDES = [
  { title: "Guide : Declarer une maladie professionnelle", description: "Étapes pour faire reconnaître votre maladie par la CPAM", category: "Guides", href: "/ressources#bibliotheque", keywords: ["guide", "declarer", "maladie", "professionnelle", "cpam", "formulaire", "cerfa", "etape", "procedure", "comment", "declaration"] },
  { title: "Guide : Se preparer a une expertise médicale", description: "Conseils et liste de controle pour votre expertise", category: "Guides", href: "/ressources#bibliotheque", keywords: ["guide", "expertise", "médicale", "préparation", "médecin", "documents", "checklist", "conseil", "astuce", "avant"] },
  { title: "Guide : Constituer un dossier MDPH", description: "Formulaire, documents et astuces pour votre demande MDPH", category: "Guides", href: "/ressources#bibliotheque", keywords: ["guide", "dossier", "mdph", "formulaire", "document", "demande", "cerfa", "constituer", "monter", "pieces"] },
  { title: "Guide : Contester un refus", description: "Droits et voies de recours — mediateur, tribunal", category: "Guides", href: "/ressources#bibliotheque", keywords: ["guide", "contester", "refus", "recours", "mediateur", "tribunal", "appel", "opposition", "rejet", "comment", "procedure", "delai"] },
  { title: "Guide : Comprendre le taux d'IPP", description: "Comment le taux est fixé et ses impacts sur l'indemnisation", category: "Guides", href: "/ressources#bibliotheque", keywords: ["guide", "ipp", "taux", "incapacité", "indemnisation", "calcul", "fixation", "bareme", "médecin", "évaluation", "pourcentage"] },
  { title: "Guide : Activer sa protection juridique", description: "Identifier et activer votre PJ — assurance, avocat", category: "Guides", href: "/ressources#bibliotheque", keywords: ["guide", "protection", "juridique", "assurance", "avocat", "pj", "activer", "contrat", "garantie", "sinistre", "declaration"] },
];

/* ── Common search intents (maps user intent to best result) ── */
const INTENTS = [
  { title: "Comment declarer un accident du travail ?", description: "Guide complet pour la declaration d'un AT auprès de l'employeur et la CPAM", category: "Guides", href: "/accident-travail-maladie-professionnelle", keywords: ["comment", "declarer", "accident", "travail", "declaration", "procedure", "24 heures", "employeur", "cerfa"] },
  { title: "Comment contester une expertise médicale ?", description: "Vos droits pour contester un rapport d'expertise defavorable", category: "Guides", href: "/expertise-medicale", keywords: ["contester", "expertise", "médicale", "rapport", "defavorable", "contre-expertise", "recours", "desaccord"] },
  { title: "Combien vais-je toucher ?", description: "Calculez votre indemnisation avec nos outils : IPP, AAH, PGPF", category: "Outils", href: "/calculatrice-ipp", keywords: ["combien", "toucher", "recevoir", "montant", "indemnite", "somme", "argent", "estimation", "calcul"] },
  { title: "Burn-out / Epuisement professionnel", description: "Le burn-out peut être reconnu comme maladie professionnelle via le CRRMP (hors tableau)", category: "Maladies professionnelles", href: "/ressources#encyclopedie", keywords: ["burn out", "burnout", "epuisement", "professionnel", "depression", "stress", "souffrance", "psychologique", "moral", "risque psychosocial", "rps"] },
  { title: "Faute inexcusable de l'employeur", description: "Procedure pour faire reconnaître la faute inexcusable et majorer votre indemnisation", category: "Indemnisation", href: "/ressources", anchor: "encyclopedie", keywords: ["faute", "inexcusable", "employeur", "majoration", "indemnisation", "procedure", "tribunal", "responsabilite", "sécurité"] },
  { title: "Consolidation — Définition", description: "Moment où l'état de santé est stabilisé — point de départ des indemnisations définitives", category: "Sections", href: "/ressources", anchor: "glossaire", keywords: ["consolidation", "stabilisation", "guerison", "fin", "arret", "date", "definition", "etat", "santé", "séquelles"] },
  { title: "Delais de prescription", description: "Les delais importants a ne pas depasser : 2 ans maladie pro, 2 mois contestation CPAM", category: "Sections", href: "/ressources", anchor: "faq", keywords: ["delai", "prescription", "2 ans", "2 mois", "temps", "limite", "date", "depasser", "trop tard", "perime"] },
];

export const SEARCH_INDEX = [
  ...TOOLS,
  ...PAGES,
  ...INTENTS,
  ...AIDES,
  ...IP_PGPF,
  ...MALADIES,
  ...TMS,
  ...IPP_ITEMS,
  ...MDPH_ITEMS,
  ...GUIDES,
];

export function searchContent(query) {
  if (!query || query.trim().length < 2) return [];
  const rawTerms = query.trim().split(/\s+/);
  const normalizedTerms = rawTerms.map(t => normalize(t));

  // Expand terms with synonyms
  const expandedTerms = new Set(normalizedTerms);
  for (const term of normalizedTerms) {
    const syns = getSynonyms(term);
    for (const s of syns) expandedTerms.add(normalize(s));
  }

  // Check for multi-word synonym match (e.g., "canal carpien")
  const fullQueryNorm = normalize(query.trim());
  const fullSyns = getSynonyms(fullQueryNorm);
  for (const s of fullSyns) expandedTerms.add(normalize(s));

  const scored = SEARCH_INDEX.map(entry => {
    // Build normalized haystack
    const haystack = normalize([
      entry.title,
      entry.description,
      ...(entry.keywords || []).map(k => typeof k === 'string' ? k : String(k))
    ].join(' '));

    let score = 0;
    let directMatches = 0;
    let synonymMatches = 0;
    const titleNorm = normalize(entry.title);
    const keywordsNorm = (entry.keywords || []).map(k => normalize(typeof k === 'string' ? k : String(k)));

    // Check each original search term
    for (const term of normalizedTerms) {
      if (term.length < 2) continue;

      // Direct match (exact substring)
      if (haystack.includes(term)) {
        directMatches++;
        // Title match gets highest boost
        if (titleNorm.includes(term)) score += 15;
        // Exact keyword match
        if (keywordsNorm.some(k => k === term)) score += 8;
        // Keyword contains term (prefix match)
        else if (keywordsNorm.some(k => k.startsWith(term) || k.includes(term))) score += 5;
        // Base haystack match
        score += 3;
      }
      // Prefix match (user typing partial word)
      else if (keywordsNorm.some(k => k.startsWith(term)) || haystack.split(/\s+/).some(w => w.startsWith(term))) {
        directMatches++;
        score += 4;
      }
      // Synonym match
      else {
        const termSyns = getSynonyms(term);
        let synFound = false;
        for (const syn of termSyns) {
          const synNorm = normalize(syn);
          if (haystack.includes(synNorm)) {
            synonymMatches++;
            synFound = true;
            if (titleNorm.includes(synNorm)) score += 8;
            else score += 3;
            break;
          }
        }
        // Check expanded terms against haystack
        if (!synFound) {
          for (const expanded of expandedTerms) {
            if (expanded.length >= 3 && haystack.includes(expanded)) {
              synonymMatches++;
              score += 2;
              break;
            }
          }
        }
      }
    }

    // Bonus: all original terms matched (directly or via synonym)
    const totalMatches = directMatches + synonymMatches;
    if (totalMatches >= normalizedTerms.filter(t => t.length >= 2).length && normalizedTerms.length > 1) {
      score += 20;
    }

    // Bonus: exact phrase match in title
    if (titleNorm.includes(fullQueryNorm)) score += 25;
    // Bonus: exact phrase match in haystack
    else if (haystack.includes(fullQueryNorm)) score += 10;

    // Category boost
    if (score > 0) {
      if (entry.category === 'Outils') score += 5;
      if (entry.category === 'Pages') score += 2;
      if (entry.category === 'Indemnisation') score += 3;
      if (entry.category === 'Guides') score += 2;
    }

    return { ...entry, score };
  })
  .filter(e => e.score > 0)
  .sort((a, b) => b.score - a.score);

  // Deduplicate by href+anchor (keep highest scored)
  const seen = new Set();
  const deduped = [];
  for (const item of scored) {
    const key = `${item.href}#${item.anchor || ''}`;
    if (seen.has(key)) continue;
    seen.add(key);
    deduped.push(item);
  }

  return deduped.slice(0, 15);
}
