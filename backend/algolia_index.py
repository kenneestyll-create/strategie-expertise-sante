"""
Algolia indexation script for Strategie & Expertise Sante.
Run: python algolia_index.py
Indexes all pages, sections, tools, guides, maladies, MDPH, aides, etc.
Configures synonyms and index settings.
"""
import os
import sys

# Load env
sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from algoliasearch.search.client import SearchClientSync
from algoliasearch.search.models.synonym_hit import SynonymHit
from algoliasearch.search.models.synonym_type import SynonymType

APP_ID = os.environ["ALGOLIA_APP_ID"]
ADMIN_KEY = os.environ["ALGOLIA_ADMIN_KEY"]
INDEX_NAME = os.environ.get("ALGOLIA_INDEX_NAME", "strategie_sante")

client = SearchClientSync(APP_ID, ADMIN_KEY)

# ──────────────────────────────────────────
# RECORDS TO INDEX
# ──────────────────────────────────────────

PAGES = [
    {"objectID": "page-accueil", "title": "Accueil", "description": "Page d'accueil de Strategie & Expertise Sante", "category": "Pages", "href": "/", "keywords": "accueil home bienvenue presentation decouvrir site"},
    {"objectID": "page-apropos", "title": "A propos — Mon parcours", "description": "Decouvrez l'experience et le parcours professionnel", "category": "Pages", "href": "/a-propos", "keywords": "parcours experience a propos qui biographie profil formation equipe competences"},
    {"objectID": "page-accompagnements", "title": "Accompagnements", "description": "Nos services d'accompagnement personnalise pour AT/MP, MDPH, expertise", "category": "Pages", "href": "/accompagnements", "keywords": "accompagnement service aide soutien conseil prestation offre suivi prise en charge"},
    {"objectID": "page-expertise", "title": "Expertise medicale", "description": "Comprendre et se preparer a l'expertise medicale — medecin expert, evaluation, rapport", "category": "Pages", "href": "/expertise-medicale", "keywords": "expertise medicale medecin conseil evaluation expert examen preparation rapport docteur avis contre-expertise"},
    {"objectID": "page-atmp", "title": "Accident du travail / Maladie professionnelle", "description": "Vos droits en cas d'AT/MP — declaration, reconnaissance, indemnisation", "category": "Pages", "href": "/accident-travail-maladie-professionnelle", "keywords": "accident travail maladie professionnelle AT MP CPAM declaration reconnaissance sinistre blessure indemnisation droit employeur securite sociale"},
    {"objectID": "page-mdph", "title": "MDPH", "description": "Tout savoir sur la Maison Departementale des Personnes Handicapees — droits, AAH, RQTH", "category": "Pages", "href": "/mdph", "keywords": "MDPH handicap maison departementale droits AAH RQTH carte invalidite PCH orientation taux incapacite reconnaissance dossier"},
    {"objectID": "page-pj", "title": "Protection juridique", "description": "Activer et utiliser votre protection juridique — avocat, recours, assurance", "category": "Pages", "href": "/protection-juridique", "keywords": "protection juridique assurance avocat recours defense PJ litige tribunal justice contrat garantie sinistre"},
    {"objectID": "page-seminaires", "title": "Seminaires", "description": "Nos seminaires de formation et d'information sante/droit", "category": "Pages", "href": "/seminaires", "keywords": "seminaire formation conference atelier evenement webinaire inscription programme"},
    {"objectID": "page-entreprises", "title": "Entreprises", "description": "Offres pour les entreprises, CSE, employeurs — prevention, formation", "category": "Pages", "href": "/entreprises", "keywords": "entreprise CSE employeur salarie prevention formation collectif groupe comite social economique"},
    {"objectID": "page-partenaires", "title": "Partenaires", "description": "Nos partenaires de confiance — reseau professionnel", "category": "Pages", "href": "/partenaires", "keywords": "partenaire reseau collaboration professionnel association"},
    {"objectID": "page-forum", "title": "Forum", "description": "Communaute d'entraide — posez vos questions, partagez votre experience", "category": "Pages", "href": "/forum", "keywords": "forum communaute discussion entraide question reponse temoignage partage echange"},
    {"objectID": "page-avis", "title": "Avis clients", "description": "Temoignages et avis de nos clients satisfaits", "category": "Pages", "href": "/avis", "keywords": "avis temoignage client satisfaction note retour experience recommandation etoile"},
    {"objectID": "page-ressources", "title": "Ressources", "description": "Base de connaissances, guides pratiques, FAQ et encyclopedie", "category": "Pages", "href": "/ressources", "keywords": "ressource guide faq information documentation encyclopedie connaissance base bibliotheque savoir"},
    {"objectID": "page-contact", "title": "Contact", "description": "Nous contacter pour une question ou un rendez-vous", "category": "Pages", "href": "/contact", "keywords": "contact email telephone message joindre ecrire appeler formulaire demande"},
    {"objectID": "page-tarifs", "title": "Tarifs", "description": "Nos tarifs et formules d'accompagnement — prix et options", "category": "Pages", "href": "/tarifs", "keywords": "tarif prix formule paiement cout pass abonnement offre montant euro budget"},
    {"objectID": "page-agenda", "title": "Prendre rendez-vous", "description": "Reserver un creneau en ligne — agenda de consultation", "category": "Pages", "href": "/agenda", "keywords": "rendez-vous agenda reserver calendrier creneau booking RDV consultation disponibilite horaire"},
    {"objectID": "page-espace-client", "title": "Espace client", "description": "Acceder a votre espace personnel securise — suivi de dossier", "category": "Pages", "href": "/espace-client", "keywords": "espace client connexion dossier suivi portail compte personnel login mot de passe"},
    {"objectID": "page-simulateur", "title": "Simulateur de droits — StrategiIA", "description": "Simulez vos droits en quelques questions grace a l'intelligence artificielle", "category": "Pages", "href": "/simulateur", "keywords": "simulateur droits eligibilite test questionnaire strategiia IA intelligence artificielle analyse diagnostic gratuit"},
    {"objectID": "page-mentions", "title": "Mentions legales", "description": "Informations legales du site", "category": "Pages", "href": "/mentions-legales", "keywords": "mentions legales RGPD donnees editeur hebergeur responsabilite"},
    {"objectID": "page-dossier-express", "title": "Dossier Express IA", "description": "Analyse complete de votre dossier par IA avec rapport PDF sous 2h — 97 euros", "category": "Pages", "href": "/dossier-express", "keywords": "dossier express analyse rapport PDF IA strategiia 97 rapide intelligence artificielle automatique premium"},
    {"objectID": "page-cgu", "title": "CGU", "description": "Conditions generales d'utilisation du site et des services", "category": "Pages", "href": "/cgu", "keywords": "CGU conditions generales utilisation reglement contrat acceptation service"},
    {"objectID": "page-confidentialite", "title": "Politique de confidentialite", "description": "Protection de vos donnees personnelles (RGPD)", "category": "Pages", "href": "/politique-confidentialite", "keywords": "RGPD confidentialite donnees protection vie privee consentement cookie personnel"},
    {"objectID": "page-parrainage", "title": "Parrainage", "description": "Programme de parrainage — parrainez un proche et beneficiez d'avantages", "category": "Pages", "href": "/parrainage", "keywords": "parrainage parrain filleul reduction avantage recommandation offre partage invitation code"},
]

TOOLS = [
    {"objectID": "tool-ipp", "title": "Calculatrice IPP", "description": "Estimez votre indemnisation selon votre taux d'incapacite permanente partielle — avec IP et PGPF", "category": "Outils", "href": "/calculatrice-ipp", "keywords": "calculatrice IPP incapacite permanente partielle indemnisation rente capital taux calcul estimation sequelles incidence professionnelle IP PGPF perte de gains futurs montant combien simuler"},
    {"objectID": "tool-aah", "title": "Calculatrice AAH", "description": "Estimez le montant de votre Allocation aux Adultes Handicapes", "category": "Outils", "href": "/calculatrice-aah", "keywords": "calculatrice AAH allocation adulte handicape montant calcul estimation invalidite revenu aide simuler combien"},
    {"objectID": "tool-simulateur", "title": "Simulateur StrategiIA", "description": "Verifiez votre eligibilite aux differentes aides et dispositifs grace a l'IA", "category": "Outils", "href": "/simulateur", "keywords": "simulateur droits eligibilite aide dispositif strategiia IA intelligence artificielle analyse diagnostic test gratuit"},
    {"objectID": "tool-dossier", "title": "Dossier Express IA", "description": "Analyse complete par intelligence artificielle avec rapport PDF — 97 euros", "category": "Outils", "href": "/dossier-express", "keywords": "dossier express IA rapport PDF analyse intelligence artificielle premium 97 rapide complet"},
    {"objectID": "tool-scanner", "title": "Scanner de documents", "description": "Numerisez vos documents medicaux avec l'appareil photo de votre telephone", "category": "Outils", "href": "/espace-client", "keywords": "scanner scan document photo numeriser appareil photo telephone camera piece justificatif medical"},
]

SECTIONS = [
    {"objectID": "sec-chiffres", "title": "Le defi en chiffres", "description": "Statistiques nationales : accidents du travail, maladies professionnelles, handicap", "category": "Sections", "href": "/", "anchor": "chiffres", "keywords": "chiffres statistiques 700000 accidents 12 millions handicap MDPH 50000 maladies donnees nombres"},
    {"objectID": "sec-services", "title": "Liste des accompagnements", "description": "Tous nos services : AT/MP, MDPH, expertise medicale, protection juridique", "category": "Sections", "href": "/accompagnements", "anchor": "services-liste", "keywords": "liste services accompagnement AT MP MDPH expertise catalogue"},
    {"objectID": "sec-regimes", "title": "Regimes speciaux (SNCF, RATP)", "description": "Accompagnement dedie aux agents des regimes speciaux", "category": "Sections", "href": "/accompagnements", "anchor": "regimes-speciaux", "keywords": "regimes speciaux SNCF RATP cheminots agents fonctionnaire public"},
    {"objectID": "sec-tarif-ia", "title": "Tarif StrategiIA", "description": "Analyse IA gratuite avec options premium des 29 euros", "category": "Sections", "href": "/tarifs", "anchor": "tarif-strategiia", "keywords": "tarif prix strategiia analyse IA 29 gratuit premium formule"},
    {"objectID": "sec-tarif-dossier", "title": "Tarif Dossier Express IA", "description": "Analyse complete par IA + rapport PDF — 97 euros", "category": "Sections", "href": "/tarifs", "anchor": "tarif-dossier-express", "keywords": "tarif prix dossier express 97 rapport PDF premium"},
    {"objectID": "sec-glossaire", "title": "Glossaire sante & droit", "description": "Lexique des termes cles : AT, MP, IPP, IP, PGPF, MDPH, AAH, RQTH", "category": "Sections", "href": "/ressources", "anchor": "glossaire", "keywords": "glossaire lexique definition AT MP IPP AAH RQTH vocabulaire IP PGPF incidence professionnelle perte de gains futurs terme signification acronyme"},
    {"objectID": "sec-encyclopedie", "title": "Encyclopedie des maladies professionnelles", "description": "Tableaux, TMS, IPP, IP, PGPF et pathologies hors tableau", "category": "Sections", "href": "/ressources", "anchor": "encyclopedie", "keywords": "encyclopedie tableaux TMS IPP pathologie maladie incidence professionnelle IP PGPF perte de gains futurs liste reference"},
    {"objectID": "sec-faq", "title": "FAQ — Questions frequentes", "description": "Reponses aux questions les plus posees", "category": "Sections", "href": "/ressources", "anchor": "faq", "keywords": "FAQ questions frequentes reponses aide comment pourquoi quand combien"},
    {"objectID": "sec-guides", "title": "Guides pratiques", "description": "Par ou commencer ? Guides etape par etape", "category": "Sections", "href": "/ressources", "anchor": "guides", "keywords": "guide pratique etape demarche commencer procedure comment faire methode"},
    {"objectID": "sec-biblio", "title": "Bibliotheque de documents", "description": "Formulaires, modeles de lettres et documents utiles", "category": "Sections", "href": "/ressources", "anchor": "bibliotheque", "keywords": "bibliotheque document formulaire lettre modele telechargement cerfa courrier template PDF"},
]

IP_PGPF = [
    {"objectID": "ip-1", "title": "Incidence Professionnelle (IP)", "description": "Indemnisation des consequences sur la carriere : penibilite accrue, devalorisation, reconversion", "category": "Indemnisation", "href": "/ressources", "anchor": "encyclopedie", "keywords": "incidence professionnelle IP penibilite devalorisation reconversion carriere indemnisation prejudice emploi consequence impact"},
    {"objectID": "pgpf-1", "title": "Perte de Gains Professionnels Futurs (PGPF)", "description": "Compensation de la perte definitive de revenus apres consolidation — capitalisation", "category": "Indemnisation", "href": "/ressources", "anchor": "encyclopedie", "keywords": "PGPF perte de gains futurs perte de gains professionnels futurs capitalisation revenus bareme Gazette du Palais rente salaire consolidation projection manque a gagner"},
    {"objectID": "ip-penibilite", "title": "Criteres IP — Penibilite accrue", "description": "Conditions de travail plus penibles dues aux sequelles : efforts supplementaires, douleurs", "category": "Indemnisation", "href": "/ressources", "anchor": "encyclopedie", "keywords": "penibilite accrue efforts douleur fatigue sequelles travail IP conditions souffrance"},
    {"objectID": "ip-devalorisation", "title": "Criteres IP — Devalorisation professionnelle", "description": "Reduction de l'employabilite suite au handicap : discrimination, postes limites", "category": "Indemnisation", "href": "/ressources", "anchor": "encyclopedie", "keywords": "devalorisation employabilite handicap discrimination embauche marche du travail IP chomage difficulte"},
    {"objectID": "pgpf-calcul", "title": "Calcul PGPF — Methode de capitalisation", "description": "Projection de carriere, evolution salariale, impact du handicap, bareme de capitalisation", "category": "Indemnisation", "href": "/ressources", "anchor": "encyclopedie", "keywords": "calcul PGPF capitalisation projection carriere salaire bareme euro de rente methode montant estimation"},
    {"objectID": "pgpa-pgpf", "title": "PGPA vs PGPF — Distinction", "description": "Perte de gains actuels (avant consolidation) vs perte de gains futurs (apres consolidation)", "category": "Indemnisation", "href": "/ressources", "anchor": "encyclopedie", "keywords": "PGPA PGPF distinction consolidation arret indemnites journalieres perte de revenus difference avant apres"},
]

AIDES = [
    {"objectID": "aide-cmi-inv", "title": "CMI Invalidite", "description": "Carte Mobilite Inclusion mention invalidite — taux superieur ou egal a 80%", "category": "Aides MDPH", "href": "/ressources", "anchor": "encyclopedie", "keywords": "CMI carte mobilite inclusion invalidite 80 handicap demi-part fiscal priorite"},
    {"objectID": "aide-cmi-prio", "title": "CMI Priorite", "description": "Carte Mobilite Inclusion mention priorite — station debout penible", "category": "Aides MDPH", "href": "/ressources", "anchor": "encyclopedie", "keywords": "CMI carte mobilite priorite station debout file d'attente place transport"},
    {"objectID": "aide-cmi-stat", "title": "CMI Stationnement", "description": "Carte Mobilite Inclusion mention stationnement — perimetre de marche limite", "category": "Aides MDPH", "href": "/ressources", "anchor": "encyclopedie", "keywords": "CMI carte stationnement parking place handicape voiture vehicule GIC"},
    {"objectID": "aide-pch-humaine", "title": "PCH — Aide humaine", "description": "Financement d'un aidant pour les actes essentiels", "category": "Aides MDPH", "href": "/ressources", "anchor": "encyclopedie", "keywords": "PCH aide humaine aidant toilette habillage alimentation prestation compensation domicile quotidien"},
    {"objectID": "aide-pch-tech", "title": "PCH — Aides techniques", "description": "Fauteuil roulant, protheses, materiel adapte", "category": "Aides MDPH", "href": "/ressources", "anchor": "encyclopedie", "keywords": "PCH aide technique fauteuil prothese materiel equipement appareillage adaptation"},
    {"objectID": "aide-pch-logement", "title": "PCH — Amenagement du logement", "description": "Rampe, douche italienne, monte-escalier, domotique", "category": "Aides MDPH", "href": "/ressources", "anchor": "encyclopedie", "keywords": "PCH logement amenagement rampe douche monte-escalier accessibilite domicile travaux maison appartement"},
    {"objectID": "aide-pch-vehicule", "title": "PCH — Amenagement du vehicule", "description": "Adaptation du vehicule et surcouts de transport", "category": "Aides MDPH", "href": "/ressources", "anchor": "encyclopedie", "keywords": "PCH vehicule voiture transport conduite adaptation permis deplacement"},
    {"objectID": "aide-aah", "title": "AAH — Allocation Adultes Handicapes", "description": "Aide financiere mensuelle (max 971 euros) pour personnes handicapees", "category": "Aides MDPH", "href": "/calculatrice-aah", "keywords": "AAH allocation adulte handicape aide financiere revenu mensuel montant argent prestation 971"},
    {"objectID": "aide-rqth", "title": "RQTH — Travailleur Handicape", "description": "Reconnaissance ouvrant des droits en emploi — amenagement de poste, Agefiph", "category": "Aides MDPH", "href": "/mdph", "keywords": "RQTH travailleur handicape emploi amenagement poste embauche Agefiph reconnaissance droit obligation quota"},
    {"objectID": "aide-hors-tableau", "title": "Reconnaissance hors tableau", "description": "Procedure de reconnaissance via le CRRMP (Alinea 3 et 4)", "category": "Maladies professionnelles", "href": "/ressources", "anchor": "encyclopedie", "keywords": "hors tableau CRRMP alinea reconnaissance comite regional maladie professionnelle procedure complementaire"},
]

GUIDES = [
    {"objectID": "guide-declarer-mp", "title": "Guide : Declarer une maladie professionnelle", "description": "Etapes pour faire reconnaitre votre maladie par la CPAM", "category": "Guides", "href": "/ressources", "anchor": "bibliotheque", "keywords": "guide declarer maladie professionnelle CPAM formulaire cerfa etape procedure comment declaration"},
    {"objectID": "guide-expertise", "title": "Guide : Se preparer a une expertise medicale", "description": "Conseils et liste de controle pour votre expertise", "category": "Guides", "href": "/ressources", "anchor": "bibliotheque", "keywords": "guide expertise medicale preparation medecin documents checklist conseil astuce avant"},
    {"objectID": "guide-mdph", "title": "Guide : Constituer un dossier MDPH", "description": "Formulaire, documents et astuces pour votre demande MDPH", "category": "Guides", "href": "/ressources", "anchor": "bibliotheque", "keywords": "guide dossier MDPH formulaire document demande cerfa constituer monter pieces"},
    {"objectID": "guide-contester", "title": "Guide : Contester un refus", "description": "Droits et voies de recours — mediateur, tribunal", "category": "Guides", "href": "/ressources", "anchor": "bibliotheque", "keywords": "guide contester refus recours mediateur tribunal appel opposition rejet comment procedure delai"},
    {"objectID": "guide-ipp", "title": "Guide : Comprendre le taux d'IPP", "description": "Comment le taux est fixe et ses impacts sur l'indemnisation", "category": "Guides", "href": "/ressources", "anchor": "bibliotheque", "keywords": "guide IPP taux incapacite indemnisation calcul fixation bareme medecin evaluation pourcentage"},
    {"objectID": "guide-pj", "title": "Guide : Activer sa protection juridique", "description": "Identifier et activer votre PJ — assurance, avocat", "category": "Guides", "href": "/ressources", "anchor": "bibliotheque", "keywords": "guide protection juridique assurance avocat PJ activer contrat garantie sinistre declaration"},
]

INTENTS = [
    {"objectID": "intent-declarer-at", "title": "Comment declarer un accident du travail ?", "description": "Guide complet pour la declaration d'un AT aupres de l'employeur et la CPAM", "category": "Guides", "href": "/accident-travail-maladie-professionnelle", "keywords": "comment declarer accident travail declaration procedure 24 heures employeur cerfa"},
    {"objectID": "intent-contester-expertise", "title": "Comment contester une expertise medicale ?", "description": "Vos droits pour contester un rapport d'expertise defavorable", "category": "Guides", "href": "/expertise-medicale", "keywords": "contester expertise medicale rapport defavorable contre-expertise recours desaccord"},
    {"objectID": "intent-combien", "title": "Combien vais-je toucher ?", "description": "Calculez votre indemnisation avec nos outils : IPP, AAH, PGPF", "category": "Outils", "href": "/calculatrice-ipp", "keywords": "combien toucher recevoir montant indemnite somme argent estimation calcul"},
    {"objectID": "intent-burnout", "title": "Burn-out / Epuisement professionnel", "description": "Le burn-out peut etre reconnu comme maladie professionnelle via le CRRMP (hors tableau)", "category": "Maladies professionnelles", "href": "/ressources", "anchor": "encyclopedie", "keywords": "burn out burnout epuisement professionnel depression stress souffrance psychologique moral risque psychosocial RPS"},
    {"objectID": "intent-faute", "title": "Faute inexcusable de l'employeur", "description": "Procedure pour faire reconnaitre la faute inexcusable et majorer votre indemnisation", "category": "Indemnisation", "href": "/ressources", "anchor": "encyclopedie", "keywords": "faute inexcusable employeur majoration indemnisation procedure tribunal responsabilite securite"},
    {"objectID": "intent-consolidation", "title": "Consolidation — Definition", "description": "Moment ou l'etat de sante est stabilise — point de depart des indemnisations definitives", "category": "Sections", "href": "/ressources", "anchor": "glossaire", "keywords": "consolidation stabilisation guerison fin arret date definition etat sante sequelles"},
    {"objectID": "intent-delais", "title": "Delais de prescription", "description": "Les delais importants a ne pas depasser : 2 ans maladie pro, 2 mois contestation CPAM", "category": "Sections", "href": "/ressources", "anchor": "faq", "keywords": "delai prescription 2 ans 2 mois temps limite date depasser trop tard perime"},
]

MALADIES = [
    {"objectID": "mal-25", "title": "Tableau 25 — Silicose", "description": "Affections consecutives a l'inhalation de poussieres de silice — delai 35 ans", "category": "Maladies professionnelles", "href": "/ressources", "anchor": "encyclopedie", "keywords": "tableau 25 silicose silice poussieres mines carrieres fonderies BTP ceramique 35 ans"},
    {"objectID": "mal-30", "title": "Tableau 30 — Amiante", "description": "Affections consecutives a l'inhalation de poussieres d'amiante — delai 40 ans", "category": "Maladies professionnelles", "href": "/ressources", "anchor": "encyclopedie", "keywords": "tableau 30 amiante poussieres flocage calorifugeage isolation mesotheliome plaque pleurale 40 ans cancer poumon"},
    {"objectID": "mal-30bis", "title": "Tableau 30 bis — Cancer broncho-pulmonaire (amiante)", "description": "Cancer provoque par l'inhalation de poussieres d'amiante — delai 40 ans", "category": "Maladies professionnelles", "href": "/ressources", "anchor": "encyclopedie", "keywords": "tableau 30 bis cancer broncho-pulmonaire amiante poumon 40 ans"},
    {"objectID": "mal-42", "title": "Tableau 42 — Surdite professionnelle", "description": "Atteinte auditive provoquee par les bruits lesionnels — delai 1 an", "category": "Maladies professionnelles", "href": "/ressources", "anchor": "encyclopedie", "keywords": "tableau 42 surdite auditive bruit lesionnel marteaux-piqueurs moteurs machines 1 an oreille"},
    {"objectID": "mal-57", "title": "Tableau 57 — TMS (Troubles musculo-squelettiques)", "description": "Affections periarticulaires provoquees par certains gestes et postures", "category": "Maladies professionnelles", "href": "/ressources", "anchor": "encyclopedie", "keywords": "tableau 57 TMS trouble musculo-squelettique gestes postures repetitifs tendinite douleur"},
    {"objectID": "mal-57a", "title": "Tableau 57A — TMS Epaule", "description": "Tendinopathie de la coiffe des rotateurs — mouvements repetes de l'epaule", "category": "Maladies professionnelles", "href": "/ressources", "anchor": "encyclopedie", "keywords": "tableau 57A TMS epaule coiffe rotateurs tendinopathie tendinite mouvement repete bras douleur"},
    {"objectID": "mal-57b", "title": "Tableau 57B — TMS Coude", "description": "Epicondylite, epitrochleite — mouvements repetes de prehension", "category": "Maladies professionnelles", "href": "/ressources", "anchor": "encyclopedie", "keywords": "tableau 57B TMS coude epicondylite epitrochleite tennis elbow golf elbow prehension vissage"},
    {"objectID": "mal-57c", "title": "Tableau 57C — TMS Poignet / Canal carpien", "description": "Syndrome du canal carpien — mouvements repetes du poignet, vibrations", "category": "Maladies professionnelles", "href": "/ressources", "anchor": "encyclopedie", "keywords": "tableau 57C TMS poignet main canal carpien syndrome nerf median flexion extension vibrations"},
    {"objectID": "mal-57d", "title": "Tableau 57D — TMS Genou", "description": "Hygroma, tendinite — travaux en position agenouillee", "category": "Maladies professionnelles", "href": "/ressources", "anchor": "encyclopedie", "keywords": "tableau 57D TMS genou hygroma tendinite agenouille accroupi rotule menisque"},
    {"objectID": "mal-57e", "title": "Tableau 57E — TMS Cheville / Pied", "description": "Tendinite d'Achille — mouvements repetes du pied, marche prolongee", "category": "Maladies professionnelles", "href": "/ressources", "anchor": "encyclopedie", "keywords": "tableau 57E TMS cheville pied tendinite Achille marche prolongee terrain"},
    {"objectID": "mal-69", "title": "Tableau 69 — Vibrations", "description": "Affections provoquees par les vibrations transmises par machines-outils — delai 5 ans", "category": "Maladies professionnelles", "href": "/ressources", "anchor": "encyclopedie", "keywords": "tableau 69 vibrations chocs machines-outils marteaux-piqueurs tronconneuses meuleuses 5 ans"},
    {"objectID": "mal-79", "title": "Tableau 79 — Menisque", "description": "Lesions chroniques du menisque — travaux agenouilles ou accroupis prolonges", "category": "Maladies professionnelles", "href": "/ressources", "anchor": "encyclopedie", "keywords": "tableau 79 menisque lesion chronique genou agenouille accroupi carreleur plombier 2 ans"},
    {"objectID": "mal-97", "title": "Tableau 97 — Lombalgie / Sciatique", "description": "Affections chroniques du rachis lombaire — manutention de charges lourdes", "category": "Maladies professionnelles", "href": "/ressources", "anchor": "encyclopedie", "keywords": "tableau 97 lombalgie sciatique rachis lombaire dos manutention charges lourdes vibrations postures 6 mois lumbago"},
    {"objectID": "mal-98", "title": "Tableau 98 — Hernie discale", "description": "Affections chroniques du rachis lombaire — hernie discale par manutention", "category": "Maladies professionnelles", "href": "/ressources", "anchor": "encyclopedie", "keywords": "tableau 98 hernie discale rachis lombaire dos manutention charges lourdes disque 6 mois"},
    {"objectID": "mal-66", "title": "Tableau 66 — Rhinites et asthmes professionnels", "description": "Exposition a des agents allergisants — farine, bois, latex, produits chimiques", "category": "Maladies professionnelles", "href": "/ressources", "anchor": "encyclopedie", "keywords": "tableau 66 rhinite asthme allergie farine bois latex chimique professionnel"},
    {"objectID": "mal-47", "title": "Tableau 47 — Bois", "description": "Affections professionnelles provoquees par les bois — menuiserie, scierie", "category": "Maladies professionnelles", "href": "/ressources", "anchor": "encyclopedie", "keywords": "tableau 47 bois menuiserie scierie ebenisterie poussieres"},
    {"objectID": "mal-36", "title": "Tableau 36 — Huiles et graisses", "description": "Affections provoquees par les huiles et graisses — usinage, mecanique", "category": "Maladies professionnelles", "href": "/ressources", "anchor": "encyclopedie", "keywords": "tableau 36 huiles graisses minerale synthese usinage metaux mecanique entretien machines"},
    {"objectID": "mal-4", "title": "Tableau 4 — Benzene", "description": "Hemopathies provoquees par le benzene — industries chimiques, petrochimie", "category": "Maladies professionnelles", "href": "/ressources", "anchor": "encyclopedie", "keywords": "tableau 4 benzene hemopathie chimie petrochimie imprimerie collage 30 ans leucemie"},
    {"objectID": "mal-6", "title": "Tableau 6 — Rayonnements ionisants", "description": "Affections provoquees par les rayonnements ionisants — nucleaire, radiologie", "category": "Maladies professionnelles", "href": "/ressources", "anchor": "encyclopedie", "keywords": "tableau 6 rayonnements ionisants nucleaire radiologie recherche 50 ans radiation"},
    {"objectID": "mal-16bis", "title": "Tableau 16 bis — Goudrons de houille", "description": "Affections cancereuses provoquees par les goudrons — travaux routiers", "category": "Maladies professionnelles", "href": "/ressources", "anchor": "encyclopedie", "keywords": "tableau 16 bis goudrons houille cancer routiers etancheite ramonage 20 ans"},
]

ALL_RECORDS = PAGES + TOOLS + SECTIONS + IP_PGPF + AIDES + GUIDES + INTENTS + MALADIES


def index_all():
    """Index all records into Algolia"""
    print(f"Indexing {len(ALL_RECORDS)} records into '{INDEX_NAME}'...")

    # Configure index settings
    client.set_settings(
        index_name=INDEX_NAME,
        index_settings={
            "searchableAttributes": [
                "title",
                "description",
                "keywords",
                "category",
            ],
            "attributesForFaceting": [
                "searchable(category)",
            ],
            "customRanking": [
                "desc(priority)",
            ],
            "typoTolerance": True,
            "minWordSizefor1Typo": 3,
            "minWordSizefor2Typos": 6,
            "hitsPerPage": 15,
            "removeStopWords": ["fr"],
            "queryLanguages": ["fr"],
            "indexLanguages": ["fr"],
            "ignorePlurals": ["fr"],
            "highlightPreTag": "<mark>",
            "highlightPostTag": "</mark>",
        },
    )
    print("Index settings configured")

    # Add priority field for ranking
    for r in ALL_RECORDS:
        if r["category"] == "Outils":
            r["priority"] = 100
        elif r["category"] == "Pages":
            r["priority"] = 80
        elif r["category"] == "Indemnisation":
            r["priority"] = 70
        elif r["category"] == "Guides":
            r["priority"] = 60
        else:
            r["priority"] = 50

    # Save all objects
    resp = client.save_objects(index_name=INDEX_NAME, objects=ALL_RECORDS)
    print(f"Indexed {len(ALL_RECORDS)} records: {resp}")

    # Configure synonyms
    synonyms = [
        {"objectID": "syn-ipp", "type": "synonym", "synonyms": ["IPP", "incapacite permanente partielle", "taux incapacite"]},
        {"objectID": "syn-at", "type": "synonym", "synonyms": ["AT", "accident du travail", "accident professionnel"]},
        {"objectID": "syn-mp", "type": "synonym", "synonyms": ["MP", "maladie professionnelle", "maladie du travail"]},
        {"objectID": "syn-mdph", "type": "synonym", "synonyms": ["MDPH", "maison departementale personnes handicapees", "maison departementale"]},
        {"objectID": "syn-aah", "type": "synonym", "synonyms": ["AAH", "allocation adulte handicape", "allocation handicap"]},
        {"objectID": "syn-docteur", "type": "synonym", "synonyms": ["docteur", "medecin", "praticien", "generaliste"]},
        {"objectID": "syn-avocat", "type": "synonym", "synonyms": ["avocat", "juriste", "conseil juridique", "defenseur"]},
        {"objectID": "syn-indemnite", "type": "synonym", "synonyms": ["indemnite", "indemnisation", "compensation", "reparation", "dedommagement"]},
        {"objectID": "syn-rente", "type": "synonym", "synonyms": ["rente", "pension", "capital", "allocation"]},
        {"objectID": "syn-salaire", "type": "synonym", "synonyms": ["salaire", "revenu", "remuneration", "gains", "paie"]},
        {"objectID": "syn-handicap", "type": "synonym", "synonyms": ["handicap", "invalidite", "incapacite", "deficience"]},
        {"objectID": "syn-sequelles", "type": "synonym", "synonyms": ["sequelles", "consequences", "blessure", "lesion", "dommage"]},
        {"objectID": "syn-recours", "type": "synonym", "synonyms": ["recours", "contestation", "appel", "opposition"]},
        {"objectID": "syn-emploi", "type": "synonym", "synonyms": ["emploi", "travail", "poste", "profession", "metier"]},
        {"objectID": "syn-dossier", "type": "synonym", "synonyms": ["dossier", "document", "formulaire", "pieces", "justificatif"]},
        {"objectID": "syn-rdv", "type": "synonym", "synonyms": ["rdv", "rendez-vous", "consultation", "creneau"]},
        {"objectID": "syn-rqth", "type": "synonym", "synonyms": ["RQTH", "reconnaissance travailleur handicape", "travailleur handicape"]},
        {"objectID": "syn-pj", "type": "synonym", "synonyms": ["PJ", "protection juridique", "assurance juridique"]},
        {"objectID": "syn-burnout", "type": "synonym", "synonyms": ["burn out", "burnout", "epuisement professionnel", "depression"]},
        {"objectID": "syn-tms", "type": "synonym", "synonyms": ["TMS", "trouble musculo-squelettique", "tendinite"]},
        {"objectID": "syn-ip", "type": "synonym", "synonyms": ["IP", "incidence professionnelle", "prejudice professionnel"]},
        {"objectID": "syn-pgpf", "type": "synonym", "synonyms": ["PGPF", "perte de gains futurs", "perte de gains professionnels futurs"]},
        {"objectID": "syn-cpam", "type": "synonym", "synonyms": ["CPAM", "securite sociale", "secu", "caisse", "assurance maladie"]},
        {"objectID": "syn-prix", "type": "synonym", "synonyms": ["prix", "tarif", "cout", "montant", "budget"]},
        {"objectID": "syn-cerfa", "type": "synonym", "synonyms": ["cerfa", "formulaire", "imprime", "document officiel"]},
        {"objectID": "syn-ia", "type": "synonym", "synonyms": ["IA", "intelligence artificielle", "strategiia"]},
        {"objectID": "syn-canal", "type": "synonym", "synonyms": ["canal carpien", "syndrome canal carpien", "nerf median", "poignet"]},
        {"objectID": "syn-pch", "type": "synonym", "synonyms": ["PCH", "prestation compensation handicap", "prestation compensation"]},
        {"objectID": "syn-cmi", "type": "synonym", "synonyms": ["CMI", "carte mobilite inclusion", "carte handicap", "carte invalidite"]},
    ]

    client.save_synonyms(index_name=INDEX_NAME, synonym_hit=synonyms, replace_existing_synonyms=True)
    print(f"Configured {len(synonyms)} synonym groups")

    print("Done! All records indexed and synonyms configured.")


if __name__ == "__main__":
    index_all()
