"""
VALIDATION MÉTIER V2 PREMIUM — StratégiIA & Dossier Express IA
Script de test avec cas métier réalistes et évaluation structurée.
"""
import asyncio, json, sys, os, time
sys.path.insert(0, '/app/backend')
from routes.strategiia import (
    STRATEGIIA_SYSTEM_PROMPT, STRATEGIIA_PREMIUM_PROMPT,
    DOSSIER_EXPRESS_SYSTEM_PROMPT, DOSSIER_EXPRESS_PROMPT
)
from emergentintegrations.llm.chat import LlmChat, UserMessage

API_KEY = "sk-emergent-cBdBa9141356f51Dd7"

# ============================================================
# CAS DE TEST STRATEGIIA (5 cas variés et réalistes)
# ============================================================
STRATEGIIA_CASES = [
    {
        "id": "S1",
        "label": "Cas simple — TMS reconnu, contestation taux IPP",
        "type_dossier": "Maladie professionnelle",
        "regime": "Regime general",
        "situation": """J'ai 52 ans, je suis cariste depuis 28 ans dans la meme entreprise de logistique. En 2021, j'ai ete reconnu en maladie professionnelle tableau 57 pour un syndrome du canal carpien bilateral. La CPAM m'a attribue un taux d'IPP de 8% a gauche et 5% a droite, soit 13% global. Mon medecin dit que c'est tres insuffisant vu mes douleurs quotidiennes. Je ne peux plus soulever de charges, j'ai des fourmillements permanents, je laisse tomber les objets. Mon employeur m'a reclasse sur un poste de bureau mais avec baisse de salaire de 400 euros par mois. Je veux savoir si je peux contester ce taux et si j'ai droit a autre chose."""
    },
    {
        "id": "S2",
        "label": "Cas flou/incomplet — AT décrit vaguement",
        "type_dossier": "Accident du travail",
        "regime": "Regime general",
        "situation": """J'ai eu un accident au travail il y a quelques mois. Je me suis fait mal au dos en portant quelque chose de lourd. J'ai ete en arret mais je ne sais pas trop ou en est mon dossier. Mon patron n'a pas voulu declarer l'accident au debut. Je ne sais pas quels sont mes droits. J'ai encore mal."""
    },
    {
        "id": "S3",
        "label": "Cas complexe — AT grave avec séquelles lourdes et potentiel élevé",
        "type_dossier": "Accident du travail",
        "regime": "Regime general",
        "situation": """J'ai 38 ans, electricien dans le BTP depuis 15 ans. Le 12 mars 2023, je suis tombe d'un echafaudage a 4 metres de hauteur sur un chantier. Fracture du plateau tibial gauche, fracture du poignet droit, 3 cotes cassees, traumatisme cranien leger. Opere 2 fois (osteosynthese genou + poignet). 14 mois d'arret de travail. Consolide en mai 2024 avec un taux d'IPP de 18%. Je boite encore, je ne peux plus monter sur les echafaudages, ni porter de charges lourdes. Mon employeur me propose un reclassement en bureau d'etudes mais je n'ai aucune formation pour ca et c'est un CDD qui se termine dans 6 mois. J'ai 3 enfants a charge. Mon avocat me dit de demander la faute inexcusable car l'echafaudage n'avait pas de garde-corps. J'ai des photos du chantier et un temoignage d'un collegue."""
    },
    {
        "id": "S4",
        "label": "Cas incohérences — Déclaration tardive, contradictions",
        "type_dossier": "Maladie professionnelle",
        "regime": "Regime general",
        "situation": """Je suis aide-soignante depuis 22 ans en EHPAD. J'ai des problemes de dos depuis 2018 (hernie discale L4-L5 confirmee par IRM). Mais je n'ai declare ma maladie professionnelle qu'en 2024 parce que je ne savais pas que c'etait possible. Le probleme c'est que mon medecin traitant a ecrit dans un certificat en 2019 que mes douleurs etaient "probablement liees au stress" sans mentionner le travail. Ensuite en 2023, un autre medecin a ecrit "lombalgie chronique d'origine professionnelle probable". La CPAM a refuse ma demande en disant que le delai de prise en charge etait depasse. Mais j'ai toujours travaille, j'ai jamais arrete, et mes douleurs sont de pire en pire. Je porte des patients tous les jours et je ne sais plus comment faire."""
    },
    {
        "id": "S5",
        "label": "Cas IP sous-exploitée — Reclassement + MDPH",
        "type_dossier": "Contestation taux IPP + MDPH",
        "regime": "Regime general",
        "situation": """J'ai 45 ans, ancienne ouvriere en usine agroalimentaire pendant 20 ans. Reconnue en MP tableau 57 (epaule droite - coiffe des rotateurs) en 2022. Taux IPP fixe a 12%. Licenciee pour inaptitude en 2023. Je suis maintenant au chomage, j'ai depose un dossier MDPH qui a ete refuse (taux d'incapacite evalue a 40%, il faut 50% pour l'AAH). Je n'arrive pas a retrouver du travail, mon epaule me fait toujours mal malgre l'operation. Je ne peux plus lever le bras au-dessus de l'horizontale. Mon ancien employeur ne m'a propose aucun reclassement serieux avant le licenciement. Je vis avec 1100 euros d'allocations chomage. Avant, je gagnais 1850 euros nets. Je ne sais pas vers qui me tourner et quels sont mes recours."""
    }
]

# ============================================================
# CAS DE TEST DOSSIER EXPRESS IA (5 cas variés et réalistes)
# ============================================================
DOSSIER_EXPRESS_CASES = [
    {
        "id": "DE1",
        "label": "Dossier bien documenté — Chronologie claire",
        "type_dossier": "Accident du travail",
        "regime": "Regime general",
        "situation": "Accident du travail sur chantier BTP",
        "documents_text": """DOCUMENT 1 — Certificat médical initial (Dr Martin, 15/03/2023)
Patient M. Dupont Jean, 42 ans. Chute d'echafaudage le 12/03/2023. Fracture du plateau tibial gauche. Fracture de Pouteau-Colles poignet droit. Fractures costales K5-K6-K7 droites. Traumatisme cranien sans perte de connaissance. Arret de travail initial 90 jours.

DOCUMENT 2 — Compte rendu operatoire (CHU Lyon, 14/03/2023)
Intervention : osteosynthese par plaque visee du plateau tibial gauche sous AG. Brochage percutane du poignet droit. Duree intervention 3h20. Suites simples. Sortie J+5.

DOCUMENT 3 — IRM genou gauche (Centre imagerie, 10/06/2023)
Consolidation osseuse en cours. Cal osseux visible. Persistance epanchement intra-articulaire modere. Menisque interne : lesion degenerative grade II. Ligament croise anterieur intact.

DOCUMENT 4 — Certificat de prolongation (Dr Martin, 12/06/2023)
Prolongation arret de travail 60 jours supplementaires. Patient presente gonalgie persistante, limitation flexion 90 degres, appui partiel avec cannes. Reeducation kinesitherapie 3x/semaine.

DOCUMENT 5 — Expertise medicale amiable CPAM (Dr Expert, 15/01/2024)
Date consolidation fixee au 15/01/2024. Sequelles : raideur genou gauche (flexion limitee a 110 degres), douleurs residuelles cotation EVA 4/10, raideur poignet droit modere, gene fonctionnelle a la marche prolongee. Taux IPP propose : 18% (12% genou + 6% poignet).

DOCUMENT 6 — Notification CPAM (02/02/2024)
Taux IPP retenu : 18%. Rente annuelle calculee base salaire 28500 euros. Capital ou rente au choix (taux >= 10%).

DOCUMENT 7 — Attestation employeur (SA Construction Plus, 20/03/2024)
M. Dupont etait employe comme electricien qualifie N3P2. Poste : travaux en hauteur, port de charges, deplacement sur chantiers. Suite inaptitude, proposition reclassement poste bureau etudes (CDD 6 mois). Baisse remuneration : 2200 brut -> 1800 brut mensuel.

DOCUMENT 8 — Temoignage collegue (M. Bernard, 25/03/2024)
J'atteste que le 12 mars 2023, l'echafaudage sur lequel travaillait Jean Dupont n'avait pas de garde-corps. Le chef de chantier nous avait dit que ce n'etait pas necessaire pour un travail de courte duree. J'ai vu Jean tomber quand une planche a cede sous ses pieds."""
    },
    {
        "id": "DE2",
        "label": "Dossier désordonné — Dates manquantes, pièces mélangées",
        "type_dossier": "Maladie professionnelle",
        "regime": "Regime general",
        "situation": "TMS multiples chez une aide-soignante",
        "documents_text": """DOCUMENT — Courrier CPAM (sans date lisible)
Madame, suite a votre demande de reconnaissance... dossier en cours d'instruction... delai reglementaire de 120 jours... necessaire d'obtenir avis CRRMP...

DOCUMENT — IRM epaule (date partiellement lisible : ...2022)
Rupture partielle du tendon sus-epineux. Bursite sous-acromiale. Arthrose acromio-claviculaire debutante.

DOCUMENT — Certificat Dr Legrand (15/09/2023)
Mme Moreau Sophie, aide-soignante. Lombalgie chronique avec sciatique L5 droite. Tendinopathie epaule droite bilaterale. Gene fonctionnelle majeure dans les gestes de la vie quotidienne et professionnelle. Patiente en arret depuis le 03/01/2023.

DOCUMENT — Lettre de l'employeur (EHPAD Les Glycines)
Nous confirmons que Mme Moreau est employee comme aide-soignante depuis 2001. Ses fonctions comportent la manutention de residents, toilettes, transferts lit-fauteuil, aide a la marche. Elle a eu plusieurs arrets de travail en 2020 et 2021 pour des problemes de dos.

DOCUMENT — Arret de travail (illisible partiellement)
Prolongation... du ...01/2023 au ...04/2023... lombalgie...

DOCUMENT — Decision CPAM (07/2024)
Refus de reconnaissance MP. Motif : delai de prise en charge depasse (tableau 98). Le CRRMP n'a pas retenu le lien direct et essentiel.

DOCUMENT — Scanner lombaire (Centre Radiologie, mars 2021)
Hernie discale L4-L5 postero-laterale droite. Protrusion L5-S1. Canal lombaire de calibre normal. Pas de compression radiculaire franche."""
    },
    {
        "id": "DE3",
        "label": "Dossier avec éléments clés peu visibles mais importants",
        "type_dossier": "Contestation taux IPP",
        "regime": "Regime general",
        "situation": "Contestation taux IPP apres AT",
        "documents_text": """DOCUMENT 1 — Notification CPAM (15/06/2023)
Taux IPP fixe a 5% suite AT du 10/01/2022. Base : sequelles canal carpien main droite.

DOCUMENT 2 — Certificat medecin traitant (Dr Petit, 20/07/2023)
Monsieur Blanc Robert, 55 ans, ouvrier en metallurgie. Sequelles canal carpien droit post-AT : douleurs persistantes face palmaire, fourmillements 3 derniers doigts, perte de force de prehension evaluee a 40% par dynamometre. Patient se plaint egalement d'insomnie due aux douleurs nocturnes. Note : le patient a ete change de poste mais effectue toujours des gestes repetitifs avec la main droite. Il signale une aggravation progressive depuis la reprise du travail en juin 2022.

DOCUMENT 3 — EMG (laboratoire neurophysiologie, 12/05/2023)
Syndrome du canal carpien droit : atteinte sensitive et motrice MODEREE A SEVERE. Vitesse de conduction sensitive nerf median : 28 m/s (normale > 50). Latence motrice distale : 6.2 ms (normale < 4.2). Conclusion : neuropathie du nerf median au canal carpien droit, stade avance, plus severe qu'attendu pour l'anciennete.

DOCUMENT 4 — Compte rendu expertise CPAM (Dr Expert, 01/06/2023)
Examen : patient droitier. Cicatrice operatoire canal carpien, bonne mobilite doigts, Tinel negatif cliniquement. Opposition pouce-auriculaire possible. Signe de Phalen non reproduit le jour de l'examen. Conclusion : sequelles moderees, pas de deficit moteur objectivable cliniquement. Taux propose : 5%.

DOCUMENT 5 — Courrier medecin du travail (10/08/2023)
Monsieur Blanc a ete vu en visite de reprise. Il presente des difficultes significatives pour tenir ses outils, serrer les boulons, et effectuer les gestes fins. J'ai recommande un amenagement de poste mais l'employeur indique que c'est techniquement impossible sur la chaine de production. Le patient exprime une anxiete importante concernant son avenir professionnel. A 55 ans et avec 30 ans d'anciennete en metallurgie, un reclassement semble tres difficile."""
    },
    {
        "id": "DE4",
        "label": "Dossier avec incohérences et contradictions internes",
        "type_dossier": "Maladie professionnelle",
        "regime": "Regime general",
        "situation": "MP avec contradictions entre les pieces",
        "documents_text": """DOCUMENT 1 — Declaration MP (05/2023)
Mme Duval Claire, coiffeuse depuis 1998. Declare dermatite de contact allergique mains — tableau 65.

DOCUMENT 2 — Certificat dermatologue (Dr Roux, 03/2023)
Eczema chronique des mains, evolution depuis environ 5 ans. Tests epicutanes positifs : thiuram mix, paraphenylenediamine. Conclusion : dermatite allergique de contact d'origine professionnelle probable.

DOCUMENT 3 — Certificat medecin traitant (Dr Faure, 01/2023)
Mme Duval, suivie pour eczema des mains depuis 2020. A noter : la patiente presente un terrain atopique connu depuis l'enfance (eczema atopique juvenile, asthme).

DOCUMENT 4 — Lettre employeur (Salon Elegance, 04/2023)
Mme Duval est employee comme coiffeuse depuis 2005 (note : la declaration indique 1998). Elle utilise quotidiennement des produits de coloration, permanente, shampoings professionnels. Des gants en latex etaient a disposition mais Mme Duval a indique ne pas les porter car cela genait ses gestes techniques.

DOCUMENT 5 — Arrets de travail
- 15/01/2022 au 30/01/2022 : eczema mains
- 10/06/2022 au 25/06/2022 : eczema mains
- 01/03/2023 au 30/04/2023 : dermatite de contact sevère
- 15/09/2023 : reprise temps partiel therapeutique

DOCUMENT 6 — Avis CRRMP (10/2023)
Apres examen du dossier, le comite note que la patiente presente un terrain atopique pre-existant. Cependant, les tests epicutanes positifs a des allergenes professionnels (thiuram, PPD) et l'aggravation en milieu professionnel sont documentes. Le comite reconnait le lien direct et essentiel.

DOCUMENT 7 — Note ergonome prevention (visite entreprise, 06/2023)
Absence de ventilation specifique dans l'espace coloration. Produits stockes sans fiches de donnees de securite visibles. Gants disponibles : latex uniquement (la patiente est possiblement allergique au latex — non teste). Aucune formation aux risques chimiques documentee pour le personnel."""
    },
    {
        "id": "DE5",
        "label": "Dossier MDPH complexe — éléments forts mais mal structurés",
        "type_dossier": "MDPH",
        "regime": "Regime general",
        "situation": "Demande MDPH refusee, recours",
        "documents_text": """DOCUMENT 1 — Notification MDPH (01/2024)
Taux d'incapacite evalue entre 50 et 79%. RQTH accordee. AAH refusee (motif non precise clairement). Orientation professionnelle : milieu ordinaire avec amenagements.

DOCUMENT 2 — Certificat psychiatre (Dr Lemoine, 11/2023)
M. Garnier Paul, 48 ans. Suivi depuis 2021 pour syndrome depressif chronique severe, avec episodes d'angoisse majeurs. Tentative de suicide en 2022 (hospitalisation 3 semaines). Traitement actuel : Sertraline 200mg, Xanax 0.5mg x3/jour, suivi psychotherapeutique hebdomadaire. Le patient presente un retrait social important, des troubles de concentration majeurs, une fatigabilite intense. Impact fonctionnel : incapable de maintenir une activite professionnelle reguliere.

DOCUMENT 3 — Rapport neuropsychologique (Centre Rehabilitation, 09/2023)
Bilan : deficits attentionnels significatifs (percentile 8), memoire de travail deficitaire (percentile 12), ralentissement ideomoteur marque. Fonctions executives alterees. Compatible avec sequelles neuropsychologiques d'un traumatisme cranien (AT 2019) et/ou impact du syndrome depressif chronique.

DOCUMENT 4 — Certificat medecin du travail (05/2023)
M. Garnier declare inapte definitivement a tout poste dans l'entreprise. Inapte a son poste de technicien de maintenance. Recommandation : pas d'activite en hauteur, pas de conduite d'engins, environnement calme avec pauses frequentes.

DOCUMENT 5 — Attestation AT (2019)
AT du 15/06/2019 : chute d'une echelle (2 metres), traumatisme cranien avec perte de connaissance. Hospitalisation 5 jours. Arret 4 mois. Taux IPP consolide a 8% (sequelles cephalalgiques).

DOCUMENT 6 — Lettre ancien employeur (12/2023)
M. Garnier Paul a ete employe comme technicien de maintenance de 2010 a 2023. Licencie pour inaptitude en octobre 2023. Aucun reclassement possible compte tenu de la configuration des postes et des restrictions medicales.

DOCUMENT 7 — Bulletins de salaire (extraits)
Avant AT (2019) : 2450 euros nets/mois
Dernier salaire (2023) : 1200 euros nets (mi-temps therapeutique)
Indemnites chomage actuelles : 980 euros/mois"""
    }
]

async def run_strategiia_test(case):
    """Run a single StrategiIA premium test."""
    chat = LlmChat(
        api_key=API_KEY,
        session_id=f"validation-{case['id']}",
        system_message=STRATEGIIA_SYSTEM_PROMPT
    ).with_model("anthropic", "claude-4-sonnet-20250514")

    user_msg = f"""Type de dossier : {case['type_dossier']}
Regime : {case['regime']}
Description de la situation : {case['situation']}

{STRATEGIIA_PREMIUM_PROMPT}"""

    msg = UserMessage(text=user_msg)
    result = await chat.send_message(msg)
    return result

async def run_dossier_express_test(case):
    """Run a single Dossier Express test."""
    chat = LlmChat(
        api_key=API_KEY,
        session_id=f"validation-{case['id']}",
        system_message=DOSSIER_EXPRESS_SYSTEM_PROMPT
    ).with_model("anthropic", "claude-4-sonnet-20250514")

    user_msg = f"""Type de dossier : {case['type_dossier']}
Regime : {case['regime']}
Description de la situation du client : {case['situation']}

CONTENU DES DOCUMENTS FOURNIS :
{case['documents_text']}

{DOSSIER_EXPRESS_PROMPT}"""

    msg = UserMessage(text=user_msg)
    result = await chat.send_message(msg)
    return result

async def main():
    results = {"strategiia": [], "dossier_express": []}
    total = len(STRATEGIIA_CASES) + len(DOSSIER_EXPRESS_CASES)
    done = 0

    print(f"=== DÉBUT VALIDATION MÉTIER V2 PREMIUM ({total} tests) ===\n")

    # StrategiIA tests
    for case in STRATEGIIA_CASES:
        print(f"[{done+1}/{total}] StrategiIA: {case['label']}...", flush=True)
        t0 = time.time()
        try:
            result = await run_strategiia_test(case)
            elapsed = round(time.time() - t0, 1)
            word_count = len(result.split())
            results["strategiia"].append({
                "id": case["id"],
                "label": case["label"],
                "word_count": word_count,
                "elapsed_seconds": elapsed,
                "output": result,
                "status": "OK"
            })
            print(f"   OK ({word_count} mots, {elapsed}s)")
        except Exception as e:
            results["strategiia"].append({
                "id": case["id"],
                "label": case["label"],
                "output": "",
                "error": str(e)[:500],
                "status": "ERROR"
            })
            print(f"   ERREUR: {str(e)[:100]}")
        done += 1

    # Dossier Express tests
    for case in DOSSIER_EXPRESS_CASES:
        print(f"[{done+1}/{total}] Dossier Express: {case['label']}...", flush=True)
        t0 = time.time()
        try:
            result = await run_dossier_express_test(case)
            elapsed = round(time.time() - t0, 1)
            word_count = len(result.split())
            results["dossier_express"].append({
                "id": case["id"],
                "label": case["label"],
                "word_count": word_count,
                "elapsed_seconds": elapsed,
                "output": result,
                "status": "OK"
            })
            print(f"   OK ({word_count} mots, {elapsed}s)")
        except Exception as e:
            results["dossier_express"].append({
                "id": case["id"],
                "label": case["label"],
                "output": "",
                "error": str(e)[:500],
                "status": "ERROR"
            })
            print(f"   ERREUR: {str(e)[:100]}")
        done += 1

    # Save results
    with open("/app/test_reports/validation_v2_raw.json", "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n=== TERMINÉ. Résultats sauvegardés dans /app/test_reports/validation_v2_raw.json ===")

if __name__ == "__main__":
    asyncio.run(main())
