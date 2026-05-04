#!/usr/bin/env python3
"""Push the 'refus-aah-rsdae-non-reconnue' SEO page to PRODUCTION.

Usage: python3 push_to_prod.py
The script will prompt for the admin password (masked input).

Requirements: Python 3.7+ with `requests` library
  pip install requests
"""
import getpass
import json
import sys

try:
    import requests
except ImportError:
    print("⚠️  Module manquant. Lancez : pip install requests")
    sys.exit(1)

API_BASE = "https://strategie-expertise-sante.fr/api"
ADMIN_EMAIL = "admin@accompagn-sante.fr"
SLUG = "refus-aah-rsdae-non-reconnue"

PAGE = {
    "slug": SLUG,
    "title": "Refus AAH pour RSDAE non reconnue : stratégie de recours",
    "meta_description": "Refus d'AAH avec un taux de 50-79 % ? La RSDAE n'a pas été reconnue. Comprenez le motif, construisez un RAPO solide, maximisez vos chances en 2026.",
    "category": "mdph",
    "intention": "refus_droits",
    "priority": "p0",
    "cta_type": "dossier_express",
    "cta_label": "Faire analyser mon refus AAH",
    "active": True,
    "content": {
        "reponse_rapide_titre": "Que signifie un refus AAH pour RSDAE non reconnue ?",
        "reponse_rapide": (
            "Le refus signifie que la CDAPH a accepté votre taux d'incapacité (entre 50 % et 79 %) "
            "mais refuse la Restriction Substantielle et Durable d'Accès à l'Emploi (RSDAE) — "
            "condition indispensable pour l'AAH au titre de l'article L.821-2 CSS. "
            "La formulation dans votre notification peut varier (« absence de RSDAE », « handicap n'interdit "
            "pas un emploi à mi-temps », ou code interne type « motif 6 » selon les MDPH) : le fond est le même. "
            "Vous disposez de 2 mois à compter de la notification pour déposer un Recours Administratif "
            "Préalable Obligatoire (RAPO). Un RAPO structuré en 3 piliers — médical, factuel, juridique — "
            "augmente significativement les chances de révision. Si le RAPO est rejeté, vous pouvez saisir "
            "le pôle social du tribunal judiciaire dans un nouveau délai de 2 mois."
        ),
        "contexte": (
            "L'AAH peut être attribuée selon deux voies (articles L.821-1 et L.821-2 du Code de la Sécurité Sociale) : "
            "un taux d'incapacité d'au moins 80 %, ou un taux compris entre 50 % et 79 % assorti d'une RSDAE reconnue. "
            "Lorsque la CDAPH accepte le taux mais refuse la RSDAE, elle rejette la demande au titre de l'article L.821-2 CSS. "
            "C'est un refus ciblé, pas une inéligibilité globale — et c'est précisément ce qui rend le recours techniquement jouable. "
            "\n\n"
            "Comment identifier ce refus dans votre notification ? La terminologie varie d'une MDPH à l'autre. "
            "On la retrouve sous différentes formes : « absence de restriction substantielle et durable d'accès à l'emploi » "
            "(la formulation la plus courante), « votre handicap n'interdit pas l'accès ou le maintien dans un emploi à au moins mi-temps », "
            "« capacités résiduelles jugées suffisantes pour un emploi adapté », ou encore des codes internes type « motif 6 » "
            "utilisés dans certains rapports d'instruction. Peu importe la formulation : dès lors que votre taux d'incapacité est "
            "reconnu entre 50 % et 79 % mais que l'AAH est refusée, vous êtes dans ce cas de figure, et la procédure de recours est identique."
        ),
        "limites": (
            "Les sites institutionnels (Service-public.fr, MDPH, CNSA) décrivent la RSDAE comme une restriction "
            "« substantielle et durable » d'accès à l'emploi. La définition reste volontairement souple. Ce qu'ils ne précisent pas, "
            "c'est que la CDAPH apprécie cette notion à partir des pièces fournies — pas de votre vécu. "
            "\n\n"
            "Concrètement : un certificat médical qui décrit un diagnostic sans détailler l'impact fonctionnel sur le travail "
            "(station debout, concentration, fatigabilité, contraintes horaires) sera lu comme une pathologie compatible avec un emploi adapté. "
            "Un projet de vie rédigé en quelques lignes génériques ne pèsera rien face à un dossier administratif standardisé. "
            "Le refus RSDAE reflète rarement la gravité réelle de votre situation — il reflète surtout les angles morts documentaires de votre dossier."
        ),
        "blocages": [
            "Le certificat médical décrit une maladie, pas ses conséquences. « Fibromyalgie » ou « lombalgie chronique » sans description des limitations concrètes (durée de station assise tolérée, fatigabilité, troubles cognitifs associés) ne démontre pas une RSDAE.",
            "Le projet de vie est absent ou trop court. La CDAPH n'a alors aucun élément pour apprécier l'impact de vos limitations sur l'accès réel à un emploi.",
            "Aucune trace des tentatives professionnelles passées. Les arrêts maladie répétés, les inaptitudes prononcées par la médecine du travail, les échecs de formation doivent figurer au dossier — ce sont des preuves concrètes d'inaccessibilité au marché du travail.",
            "Le contexte environnemental est occulté. Territoire rural, absence de transports adaptés, impossibilité de déménager — ces éléments renforcent la démonstration de RSDAE quand ils sont documentés.",
            "Le RAPO reproduit le dossier initial. Redéposer les mêmes pièces conduit mécaniquement au même refus. Le recours ne fonctionne qu'avec des éléments nouveaux ou réorganisés.",
        ],
        "erreurs": [
            "Laisser passer les 2 mois de délai RAPO : au-delà, la décision devient définitive et non contestable (article L.142-4 CSS).",
            "Croire qu'un taux élevé déclenche automatiquement la RSDAE. Le taux et la RSDAE sont deux critères distincts évalués séparément.",
            "Envoyer un courrier manuscrit non structuré. Le RAPO s'apprécie à la lisibilité : structure claire, numérotation des pièces, référence aux articles de loi.",
            "Oublier l'envoi en recommandé avec accusé de réception. Sans preuve de dépôt, le délai n'est pas opposable à la MDPH.",
            "Attendre le silence pour saisir le tribunal. Le silence de la MDPH pendant 2 mois vaut rejet implicite (et non acceptation — article R.421-2 du Code de justice administrative, applicable par renvoi).",
        ],
        "strategie": (
            "Un RAPO efficace repose sur trois étages complémentaires, pas sur la répétition du dossier initial. "
            "Pilier médical : un certificat actualisé rédigé par votre spécialiste (pas seulement le médecin traitant), "
            "détaillant les limitations fonctionnelles en lien explicite avec l'emploi — durée de station debout tolérée, "
            "capacité de concentration continue, fatigabilité post-effort, intolérances environnementales, effets des traitements en cours. "
            "Pilier factuel : la chronologie documentée de votre vie professionnelle — arrêts maladie, avis d'inaptitude de la médecine du travail, "
            "tentatives de reclassement, formations interrompues, bilans Pôle emploi ou Cap emploi. Chaque pièce doit être datée, nominative, "
            "cohérente avec la période décrite par le certificat médical. Pilier juridique : le rappel ciblé de l'article L.821-2 CSS (RSDAE) "
            "et de l'article L.114-1 CASF (définition du handicap), suivi d'une démonstration courte reliant vos pièces aux critères légaux. "
            "C'est le fond qui convainc, pas la longueur."
        ),
        "orientation": [
            "Relisez votre notification pour identifier la formulation exacte du refus (absence de RSDAE, code interne, autre) et notez la date de notification — elle déclenche le délai de 2 mois.",
            "Demandez à la MDPH l'intégralité du dossier d'instruction (rapport médical, synthèse CDAPH) : c'est un droit, utile pour identifier les lacunes à combler.",
            "Rassemblez les nouveaux éléments : certificat médical actualisé ciblé emploi, chronologie professionnelle documentée, avis spécialisés (ergothérapeute, psychologue, médecine du travail).",
            "Rédigez le RAPO structuré en 3 piliers (médical, factuel, juridique) et envoyez-le en recommandé avec accusé de réception à la MDPH, dans le délai de 2 mois.",
            "Préparez en parallèle la saisine du pôle social du tribunal judiciaire : si le RAPO est rejeté ou reste sans réponse pendant 2 mois, vous disposez de 2 mois supplémentaires pour saisir la juridiction (article L.142-8 CSS).",
        ],
        "reassurance": (
            "Le refus AAH pour RSDAE non reconnue est l'une des décisions les plus contestables parmi les refus MDPH, "
            "précisément parce que la RSDAE laisse une marge d'appréciation importante à la CDAPH. Un dossier correctement "
            "restructuré, avec des pièces médicales ciblant l'emploi et une chronologie factuelle claire, peut faire basculer "
            "la décision au stade du RAPO — sans nécessairement passer par le tribunal."
        ),
        "maillage": [
            {"slug": "refus-mdph-aah-que-faire", "text": "Refus MDPH AAH : recours, délais et solutions"},
            {"slug": "recours-tribunal-judiciaire-pole-social", "text": "Recours devant le tribunal judiciaire : procédure et enjeux"},
            {"slug": "comment-demander-rqth-strategic", "text": "RQTH : stratégie d'accès aux droits"},
        ],
        "faq": [
            {
                "question": "Comment reconnaître un refus AAH pour RSDAE non reconnue ?",
                "answer": "Si votre notification indique un taux d'incapacité reconnu entre 50 % et 79 % mais refuse l'AAH, c'est que la RSDAE n'a pas été reconnue. Les formulations varient selon les MDPH (« absence de RSDAE », « handicap n'interdit pas un emploi à mi-temps », ou code interne type « motif 6 »). Le fond juridique et la procédure de recours sont identiques.",
            },
            {
                "question": "Le silence de la MDPH après mon RAPO vaut-il acceptation ?",
                "answer": "Non. Le silence gardé pendant 2 mois sur un RAPO MDPH vaut rejet implicite (article R.421-2 CJA, applicable par renvoi). Dès ce rejet implicite, vous disposez de 2 mois pour saisir le pôle social du tribunal judiciaire.",
            },
            {
                "question": "Puis-je contester le refus sans avocat ?",
                "answer": "Oui. Le RAPO est gratuit et ne nécessite aucun avocat. Devant le pôle social du tribunal judiciaire, l'assistance d'un avocat n'est pas obligatoire, mais un accompagnement stratégique (dossier, pièces, argumentaire) est un facteur déterminant.",
            },
            {
                "question": "Quels documents médicaux ajouter dans un RAPO pour RSDAE ?",
                "answer": "Privilégiez un certificat médical actualisé rédigé par un spécialiste, décrivant les limitations fonctionnelles liées à l'emploi (durée de station, concentration, fatigabilité). Ajoutez les avis de la médecine du travail, les comptes rendus d'ergothérapie, de kinésithérapie, de psychologie si pertinents. Évitez la simple reconduction du certificat initial.",
            },
            {
                "question": "Faut-il attendre la réponse au RAPO avant de saisir le tribunal ?",
                "answer": "Vous devez attendre soit la notification de rejet du RAPO, soit l'expiration du délai de 2 mois (qui vaut rejet implicite). Vous ne pouvez pas saisir le tribunal en même temps — le RAPO est un préalable obligatoire (article L.142-4 CSS).",
            },
            {
                "question": "La MDPH peut-elle rejeter mon RAPO avec les mêmes arguments ?",
                "answer": "Si vous redéposez le dossier identique, oui — le refus sera probablement confirmé. Mais si vous apportez des éléments nouveaux (certificats actualisés, chronologie professionnelle, avis spécialisés supplémentaires), la CDAPH est tenue de réexaminer la RSDAE à la lumière de ces pièces.",
            },
            {
                "question": "Puis-je demander une expertise médicale indépendante ?",
                "answer": "Le médecin que vous consultez pour rédiger le certificat d'appui au RAPO ne doit pas être le médecin MDPH ayant instruit le dossier initial. Devant le tribunal judiciaire, une expertise médicale judiciaire peut être ordonnée — elle est alors contradictoire (article R.141-1 CSS).",
            },
            {
                "question": "Combien de temps dure la procédure complète ?",
                "answer": "Comptez 2 à 4 mois pour la réponse au RAPO selon la MDPH, puis 6 à 12 mois en moyenne pour une décision du pôle social si le recours contentieux est engagé. Le calendrier exact dépend de votre département.",
            },
        ],
    },
}


def main():
    print("=" * 60)
    print("  PUSH ARTICLE EN PRODUCTION")
    print("  Stratégie & Expertise Santé")
    print("=" * 60)
    print(f"\n  Cible : {API_BASE}")
    print(f"  Article : /guide/{SLUG}")
    print(f"  Admin   : {ADMIN_EMAIL}\n")

    password = getpass.getpass("  Mot de passe admin : ")
    if not password:
        print("\n❌ Mot de passe vide. Annulation.")
        sys.exit(1)

    # 1. Authentification
    print("\n[1/3] Authentification…")
    try:
        r = requests.post(
            f"{API_BASE}/auth/login",
            json={"email": ADMIN_EMAIL, "password": password},
            timeout=15,
        )
    except Exception as e:
        print(f"❌ Erreur réseau : {e}")
        sys.exit(1)

    if r.status_code != 200:
        print(f"❌ Login échoué (HTTP {r.status_code}) : {r.text[:200]}")
        sys.exit(1)

    token = r.json().get("access_token") or r.json().get("token")
    if not token:
        print(f"❌ Token absent dans la réponse : {r.text[:200]}")
        sys.exit(1)
    print("    ✓ Authentifié")

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # 2. Vérifier si la page existe déjà
    print("\n[2/3] Vérification existence…")
    check = requests.get(f"{API_BASE}/guide/{SLUG}", timeout=10)
    if check.status_code == 200:
        print("    ⚠️  La page existe déjà en production. Mise à jour via PUT…")
        r2 = requests.put(
            f"{API_BASE}/admin/seo-pages/{SLUG}",
            json=PAGE,
            headers=headers,
            timeout=30,
        )
        if r2.status_code in (200, 204):
            print("    ✓ Page mise à jour")
        else:
            print(f"❌ Mise à jour échouée (HTTP {r2.status_code}) : {r2.text[:300]}")
            sys.exit(1)
    else:
        # 3. Création
        print("    → Page absente, création en cours…")
        print("\n[3/3] Création de la page SEO…")
        r3 = requests.post(
            f"{API_BASE}/admin/seo-pages",
            json=PAGE,
            headers=headers,
            timeout=30,
        )
        if r3.status_code != 200 and r3.status_code != 201:
            print(f"❌ Création échouée (HTTP {r3.status_code}) : {r3.text[:300]}")
            sys.exit(1)
        print("    ✓ Page créée")

    # Vérification finale
    print("\n[Vérif] Test de l'URL publique…")
    final = requests.get(f"{API_BASE}/guide/{SLUG}", timeout=10)
    if final.status_code == 200:
        data = final.json()
        print(f"    ✓ HTTP 200 — Title: {data.get('title')}")
        print(f"    ✓ FAQ items: {len(data.get('content', {}).get('faq', []))}")
        print(f"    ✓ Maillage entrant : {len(data.get('content', {}).get('maillage', []))}")
    else:
        print(f"⚠️  Vérification finale : HTTP {final.status_code}")

    print("\n" + "=" * 60)
    print("  ✅ TERMINÉ")
    print(f"  → https://strategie-expertise-sante.fr/guide/{SLUG}")
    print("  Vous pouvez maintenant le soumettre à Google Search Console")
    print("=" * 60)


if __name__ == "__main__":
    main()
