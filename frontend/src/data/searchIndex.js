import { MALADIES_PRO_TABLEAUX, TMS_LOCALISATION, IPP_EXEMPLES } from './maladiesProfessionnelles';
import { MDPH_DIRECTORY } from './mdphDirectory';

/*
  Each entry: { title, description, category, href, keywords[], anchor? }
  - category groups results visually
  - keywords are used for matching (lowercased at search time)
  - href is where the user navigates on click
  - anchor (optional) is an element id to scroll to on the target page
*/

const PAGES = [
  { title: "Accueil", description: "Page d'accueil de Stratégie & Expertise Santé", category: "Pages", href: "/", keywords: ["accueil", "home", "bienvenue"] },
  { title: "À propos — Mon parcours", description: "Découvrez l'expérience et le parcours professionnel", category: "Pages", href: "/a-propos", keywords: ["parcours", "expérience", "à propos", "qui", "biographie"] },
  { title: "Accompagnements", description: "Nos services d'accompagnement personnalisé", category: "Pages", href: "/accompagnements", keywords: ["accompagnement", "service", "aide", "soutien", "conseil"] },
  { title: "Expertise médicale", description: "Comprendre et se préparer à l'expertise médicale", category: "Pages", href: "/expertise-medicale", keywords: ["expertise", "médicale", "médecin", "conseil", "évaluation", "expert"] },
  { title: "Accident du travail / Maladie professionnelle", description: "Vos droits en cas d'AT/MP", category: "Pages", href: "/accident-travail-maladie-professionnelle", keywords: ["accident", "travail", "maladie", "professionnelle", "AT", "MP", "CPAM", "déclaration", "reconnaissance"] },
  { title: "MDPH", description: "Tout savoir sur la Maison Départementale des Personnes Handicapées", category: "Pages", href: "/mdph", keywords: ["mdph", "handicap", "maison départementale", "droits", "AAH", "RQTH", "carte", "invalidité"] },
  { title: "Protection juridique", description: "Activer et utiliser votre protection juridique", category: "Pages", href: "/protection-juridique", keywords: ["protection", "juridique", "assurance", "avocat", "recours", "défense"] },
  { title: "Séminaires", description: "Nos séminaires de formation et d'information", category: "Pages", href: "/seminaires", keywords: ["séminaire", "formation", "conférence", "atelier"] },
  { title: "Entreprises", description: "Offres pour les entreprises et les CSE", category: "Pages", href: "/entreprises", keywords: ["entreprise", "CSE", "employeur", "salarié", "prévention"] },
  { title: "Partenaires", description: "Nos partenaires de confiance", category: "Pages", href: "/partenaires", keywords: ["partenaire", "réseau", "collaboration"] },
  { title: "Forum", description: "Communauté d'entraide entre usagers", category: "Pages", href: "/forum", keywords: ["forum", "communauté", "discussion", "entraide", "question"] },
  { title: "Avis clients", description: "Témoignages et avis de nos clients", category: "Pages", href: "/avis", keywords: ["avis", "témoignage", "client", "satisfaction", "note"] },
  { title: "Ressources", description: "Base de connaissances, guides et FAQ", category: "Pages", href: "/ressources", keywords: ["ressource", "guide", "faq", "information", "documentation", "encyclopédie"] },
  { title: "Contact", description: "Nous contacter pour une question ou un rendez-vous", category: "Pages", href: "/contact", keywords: ["contact", "email", "téléphone", "message", "joindre"] },
  { title: "Tarifs", description: "Nos tarifs et formules d'accompagnement", category: "Pages", href: "/tarifs", keywords: ["tarif", "prix", "formule", "paiement", "coût", "pass"] },
  { title: "Prendre rendez-vous", description: "Réserver un créneau en ligne", category: "Pages", href: "/agenda", keywords: ["rendez-vous", "agenda", "réserver", "calendrier", "créneau", "booking"] },
  { title: "Espace client", description: "Accéder à votre espace personnel sécurisé", category: "Pages", href: "/espace-client", keywords: ["espace client", "connexion", "dossier", "suivi", "portail"] },
  { title: "Simulateur de droits", description: "Simulez vos droits en quelques questions", category: "Pages", href: "/simulateur", keywords: ["simulateur", "droits", "éligibilité", "test", "questionnaire"] },
  { title: "Mentions légales", description: "Informations légales du site", category: "Pages", href: "/mentions-legales", keywords: ["mentions", "légales", "RGPD", "données"] },
  { title: "Dossier Express IA", description: "Analyse complète de votre dossier par IA avec rapport PDF sous 2h - 97€", category: "Pages", href: "/dossier-express", keywords: ["dossier", "express", "analyse", "rapport", "PDF", "IA", "stratégiia", "97", "rapide"] },
  { title: "CGU", description: "Conditions générales d'utilisation", category: "Pages", href: "/cgu", keywords: ["CGU", "conditions", "générales", "utilisation"] },
  { title: "Politique de confidentialité", description: "Protection de vos données personnelles (RGPD)", category: "Pages", href: "/politique-confidentialite", keywords: ["RGPD", "confidentialité", "données", "protection", "vie privée", "consentement"] },
  { title: "Le défi en chiffres", description: "Statistiques nationales : accidents du travail, maladies professionnelles, handicap, MDPH", category: "Pages", href: "/", anchor: "chiffres", keywords: ["chiffres", "statistiques", "700000", "accidents", "12 millions", "handicap", "MDPH", "50000", "maladies"] },
  // Anchored sections
  { title: "Liste des accompagnements", description: "Tous nos services : AT/MP, MDPH, expertise médicale, protection juridique", category: "Sections", href: "/accompagnements", anchor: "services-liste", keywords: ["liste", "services", "accompagnement", "AT", "MP", "MDPH", "expertise"] },
  { title: "Régimes spéciaux (SNCF, RATP)", description: "Accompagnement dédié aux agents des régimes spéciaux", category: "Sections", href: "/accompagnements", anchor: "regimes-speciaux", keywords: ["régimes", "spéciaux", "SNCF", "RATP", "cheminots", "agents"] },
  { title: "Tarif StrategiIA", description: "Analyse IA gratuite avec options premium dès 29€", category: "Sections", href: "/tarifs", anchor: "tarif-strategiia", keywords: ["tarif", "prix", "strategiia", "analyse", "IA", "29"] },
  { title: "Tarif Dossier Express IA", description: "Analyse complète par IA + rapport PDF — 97€", category: "Sections", href: "/tarifs", anchor: "tarif-dossier-express", keywords: ["tarif", "prix", "dossier", "express", "97", "rapport"] },
  { title: "Glossaire santé & droit", description: "Lexique des termes clés : AT, MP, IPP, MDPH, AAH, RQTH", category: "Sections", href: "/ressources", anchor: "glossaire", keywords: ["glossaire", "lexique", "définition", "AT", "MP", "IPP", "AAH", "RQTH", "vocabulaire"] },
  { title: "Encyclopédie des maladies professionnelles", description: "Tableaux, TMS, IPP et pathologies hors tableau", category: "Sections", href: "/ressources", anchor: "encyclopedie", keywords: ["encyclopédie", "tableaux", "TMS", "IPP", "pathologie", "maladie"] },
  { title: "FAQ — Questions fréquentes", description: "Réponses aux questions les plus posées", category: "Sections", href: "/ressources", anchor: "faq", keywords: ["FAQ", "questions", "fréquentes", "réponses", "aide"] },
  { title: "Guides pratiques", description: "Par où commencer ? Guides étape par étape", category: "Sections", href: "/ressources", anchor: "guides", keywords: ["guide", "pratique", "étape", "démarche", "commencer"] },
  { title: "Bibliothèque de documents", description: "Formulaires, modèles de lettres et documents utiles", category: "Sections", href: "/ressources", anchor: "bibliotheque", keywords: ["bibliothèque", "document", "formulaire", "lettre", "modèle", "téléchargement"] },
];

const TOOLS = [
  { title: "Calculatrice IPP", description: "Estimez votre indemnisation selon votre taux d'incapacité permanente partielle", category: "Outils", href: "/calculatrice-ipp", keywords: ["calculatrice", "IPP", "incapacité", "permanente", "partielle", "indemnisation", "rente", "capital", "taux", "calcul", "estimation", "séquelles"] },
  { title: "Calculatrice AAH", description: "Estimez le montant de votre Allocation aux Adultes Handicapés", category: "Outils", href: "/calculatrice-aah", keywords: ["calculatrice", "AAH", "allocation", "adulte", "handicapé", "montant", "calcul", "estimation", "invalidité", "revenu"] },
  { title: "Simulateur de droits", description: "Vérifiez votre éligibilité aux différentes aides et dispositifs", category: "Outils", href: "/simulateur", keywords: ["simulateur", "droits", "éligibilité", "aide", "dispositif"] },
];

const MALADIES = MALADIES_PRO_TABLEAUX.map(m => ({
  title: `Tableau ${m.numero} — ${m.titre}`,
  description: `Délai : ${m.delai} | ${m.travaux}`,
  category: "Maladies professionnelles",
  href: "/ressources#encyclopedie",
  keywords: [
    m.numero, m.titre.toLowerCase(), m.travaux.toLowerCase(), m.delai.toLowerCase(),
    "tableau", "maladie", "professionnelle"
  ].join(' ').split(/[\s,()]+/).filter(Boolean)
}));

const TMS = TMS_LOCALISATION.map(t => ({
  title: `TMS ${t.tableau} — ${t.zone}`,
  description: t.pathologies.join(', '),
  category: "Maladies professionnelles",
  href: "/ressources#encyclopedie",
  keywords: [
    t.tableau.toLowerCase(), t.zone.toLowerCase(),
    ...t.pathologies.map(p => p.toLowerCase()),
    "tms", "trouble", "musculo", "squelettique", "tableau 57"
  ]
}));

const IPP_ITEMS = IPP_EXEMPLES.map(ex => ({
  title: `IPP ${ex.taux}% — ${ex.description}`,
  description: ex.indemnisation,
  category: "IPP — Exemples",
  href: "/ressources#encyclopedie",
  keywords: [
    `${ex.taux}%`, ex.description.toLowerCase(), ex.indemnisation.toLowerCase(),
    "ipp", "incapacité", "taux", "indemnisation", "exemple"
  ]
}));

const MDPH_ITEMS = MDPH_DIRECTORY.map(m => ({
  title: `MDPH ${m.nom} (${m.dep})`,
  description: m.adresse,
  category: "Annuaire MDPH",
  href: "/ressources#encyclopedie",
  keywords: [m.dep.toLowerCase(), m.nom.toLowerCase(), "mdph", "maison", "département", "handicap", "adresse"]
}));

const AIDES = [
  { title: "CMI Invalidité", description: "Carte Mobilité Inclusion mention invalidité — taux ≥ 80%", category: "Aides MDPH", href: "/ressources#encyclopedie", keywords: ["cmi", "carte", "mobilité", "inclusion", "invalidité", "80%", "handicap", "demi-part"] },
  { title: "CMI Priorité", description: "Carte Mobilité Inclusion mention priorité — station debout pénible", category: "Aides MDPH", href: "/ressources#encyclopedie", keywords: ["cmi", "carte", "mobilité", "priorité", "station debout", "file d'attente"] },
  { title: "CMI Stationnement", description: "Carte Mobilité Inclusion mention stationnement — périmètre de marche limité", category: "Aides MDPH", href: "/ressources#encyclopedie", keywords: ["cmi", "carte", "stationnement", "parking", "place handicapé", "voiture"] },
  { title: "PCH — Aide humaine", description: "Financement d'un aidant pour les actes essentiels", category: "Aides MDPH", href: "/ressources#encyclopedie", keywords: ["pch", "aide", "humaine", "aidant", "toilette", "habillage", "alimentation", "prestation compensation"] },
  { title: "PCH — Aides techniques", description: "Fauteuil roulant, prothèses, matériel adapté", category: "Aides MDPH", href: "/ressources#encyclopedie", keywords: ["pch", "aide", "technique", "fauteuil", "prothèse", "matériel", "équipement"] },
  { title: "PCH — Aménagement du logement", description: "Rampe, douche italienne, monte-escalier, domotique", category: "Aides MDPH", href: "/ressources#encyclopedie", keywords: ["pch", "logement", "aménagement", "rampe", "douche", "monte-escalier", "accessibilité", "domicile"] },
  { title: "PCH — Aménagement du véhicule", description: "Adaptation du véhicule et surcoûts de transport", category: "Aides MDPH", href: "/ressources#encyclopedie", keywords: ["pch", "véhicule", "voiture", "transport", "conduite", "adaptation"] },
  { title: "AAH — Allocation Adultes Handicapés", description: "Aide financière mensuelle (max 971,37 €) pour personnes handicapées", category: "Aides MDPH", href: "/calculatrice-aah", keywords: ["aah", "allocation", "adulte", "handicapé", "aide", "financière", "revenu", "mensuel"] },
  { title: "RQTH — Travailleur Handicapé", description: "Reconnaissance ouvrant des droits en emploi", category: "Aides MDPH", href: "/mdph", keywords: ["rqth", "travailleur", "handicapé", "emploi", "aménagement", "poste", "embauche", "agefiph"] },
  { title: "Reconnaissance hors tableau", description: "Procédure de reconnaissance via le CRRMP (Alinéa 3 et 4)", category: "Maladies professionnelles", href: "/ressources#encyclopedie", keywords: ["hors tableau", "crrmp", "alinéa", "reconnaissance", "comité", "régional", "maladie", "professionnelle"] },
];

const GUIDES = [
  { title: "Guide : Déclarer une maladie professionnelle", description: "Étapes pour faire reconnaître votre maladie par la CPAM", category: "Guides", href: "/ressources#bibliotheque", keywords: ["guide", "déclarer", "maladie", "professionnelle", "cpam", "formulaire", "cerfa"] },
  { title: "Guide : Se préparer à une expertise médicale", description: "Conseils et liste de contrôle", category: "Guides", href: "/ressources#bibliotheque", keywords: ["guide", "expertise", "médicale", "préparation", "médecin", "documents"] },
  { title: "Guide : Constituer un dossier MDPH", description: "Formulaire, documents et astuces", category: "Guides", href: "/ressources#bibliotheque", keywords: ["guide", "dossier", "mdph", "formulaire", "document", "demande"] },
  { title: "Guide : Contester un refus", description: "Droits et voies de recours", category: "Guides", href: "/ressources#bibliotheque", keywords: ["guide", "contester", "refus", "recours", "médiateur", "tribunal"] },
  { title: "Guide : Comprendre le taux d'IPP", description: "Comment le taux est fixé et ses impacts", category: "Guides", href: "/ressources#bibliotheque", keywords: ["guide", "ipp", "taux", "incapacité", "indemnisation", "calcul"] },
  { title: "Guide : Activer sa protection juridique", description: "Identifier et activer votre PJ", category: "Guides", href: "/ressources#bibliotheque", keywords: ["guide", "protection", "juridique", "assurance", "avocat", "pj"] },
];

export const SEARCH_INDEX = [
  ...TOOLS,
  ...PAGES,
  ...AIDES,
  ...MALADIES,
  ...TMS,
  ...IPP_ITEMS,
  ...MDPH_ITEMS,
  ...GUIDES,
];

export function searchContent(query) {
  if (!query || query.trim().length < 2) return [];
  const terms = query.toLowerCase().trim().split(/\s+/);

  const scored = SEARCH_INDEX.map(entry => {
    const haystack = [
      entry.title.toLowerCase(),
      entry.description.toLowerCase(),
      ...(entry.keywords || []).map(k => typeof k === 'string' ? k.toLowerCase() : k)
    ].join(' ');

    let score = 0;
    let allMatch = true;
    for (const term of terms) {
      if (haystack.includes(term)) {
        // Boost for title match
        if (entry.title.toLowerCase().includes(term)) score += 10;
        // Boost for exact keyword match
        if (entry.keywords?.some(k => k === term)) score += 5;
        // Base match
        score += 3;
      } else {
        allMatch = false;
      }
    }

    // Bonus for matching ALL terms
    if (allMatch && terms.length > 1) score += 15;

    // Category boost only when there's at least one real match
    if (score > 0) {
      if (entry.category === 'Outils') score += 5;
      if (entry.category === 'Pages') score += 2;
    }

    return { ...entry, score };
  })
  .filter(e => e.score > 0)
  .sort((a, b) => b.score - a.score);

  // Limit to top 15 results
  return scored.slice(0, 15);
}
