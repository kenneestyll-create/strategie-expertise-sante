from typing import Optional

from emergentintegrations.llm.chat import LlmChat, UserMessage

from config import EMERGENT_LLM_KEY, logger


FAQ_DATABASE = {
    "expertise médicale": {
        "keywords": ["expertise", "médical", "médecin", "expert", "préparer", "préparation"],
        "response": """**Comment se préparer à une expertise médicale ?**

Voici les étapes essentielles :

1. **Rassemblez vos documents** : tous vos certificats médicaux, comptes-rendus, imageries, ordonnances
2. **Préparez une chronologie** de votre parcours médical
3. **Listez vos symptômes** au quotidien et leur impact sur votre vie
4. **Notez vos questions** pour l'expert
5. **Restez honnête et précis** dans vos réponses

L'expertise dure généralement 30 à 60 minutes. Vous pouvez vous faire accompagner.

👉 [Découvrez notre accompagnement personnalisé](/expertise-medicale)"""
    },
    "mdph": {
        "keywords": ["mdph", "handicap", "rqth", "aah", "allocation", "reconnaissance"],
        "response": """**Qu'est-ce que la MDPH ?**

La **Maison Départementale des Personnes Handicapées** est votre interlocuteur unique pour :

- La **RQTH** (Reconnaissance de la Qualité de Travailleur Handicapé)
- L'**AAH** (Allocation aux Adultes Handicapés)
- Les **cartes d'invalidité** et de stationnement
- Les aides humaines et matérielles

**Pour constituer un dossier :**
1. Téléchargez le formulaire unique sur le site de votre MDPH
2. Faites remplir le certificat médical par votre médecin
3. Joignez tous les justificatifs demandés

Délai moyen : 4 à 6 mois.

👉 [En savoir plus sur les démarches MDPH](/mdph)"""
    },
    "accident travail": {
        "keywords": ["accident", "travail", "at", "mp", "maladie", "professionnelle", "droits", "droit"],
        "response": """**Quels sont vos droits après un accident du travail ?**

En cas d'AT/MP, vous avez droit à :

- **Prise en charge à 100%** des soins liés à l'accident
- **Indemnités journalières** pendant l'arrêt de travail
- **Rente ou capital** en cas de séquelles permanentes (IPP)
- **Protection contre le licenciement** pendant l'arrêt

**Étapes clés :**
1. Déclaration dans les 24h à l'employeur
2. Certificat médical initial
3. Suivi médical et consolidation
4. Évaluation du taux d'IPP

👉 [Comprendre vos droits AT/MP](/accident-travail-maladie-professionnelle)"""
    },
    "protection juridique": {
        "keywords": ["protection", "juridique", "assurance", "avocat", "activer", "litige"],
        "response": """**Comment activer votre protection juridique ?**

La protection juridique est souvent incluse dans vos contrats d'assurance (habitation, auto, santé). Elle peut couvrir les frais d'avocat et d'expertise.

**Pour l'activer :**
1. Vérifiez vos contrats d'assurance
2. Identifiez les garanties couvertes
3. Déclarez votre litige par écrit à l'assureur
4. Constituez votre dossier

**Bon à savoir :** Vous avez le droit de choisir votre propre avocat, même si l'assurance vous en propose un.

👉 [Guide complet sur la protection juridique](/protection-juridique)"""
    },
    "tarifs": {
        "keywords": ["tarif", "prix", "coût", "combien", "prestation", "accompagnement"],
        "response": """**Nos tarifs**

- **Analyse de dossier** : à partir de 150 €
- **Préparation à expertise médicale** : à partir de 250 €
- **Accompagnement MDPH** : à partir de 200 €
- **Protection juridique** : à partir de 200 €
- **Accompagnement complet** : à partir de 500 € (sur devis)
- **Séminaires / Formations** : sur devis
- **Conseil entreprises** : sur devis

**Le premier échange téléphonique est gratuit et sans engagement.**

👉 [Voir tous nos tarifs](/tarifs)"""
    },
    "contact": {
        "keywords": ["contact", "rendez-vous", "joindre", "téléphone", "email", "contacter"],
        "response": """**Comment nous contacter ?**

Vous pouvez me contacter pour un premier échange gratuit et sans engagement :

- **Par le formulaire de contact** sur notre site
- **Par email** : contact@accompagn-sante.fr
- **Par téléphone** : 06 00 00 00 00

Je vous répondrai dans les 24 à 48 heures.

👉 [Accéder au formulaire de contact](/contact)"""
    }
}


def find_faq_response(message: str) -> Optional[str]:
    message_lower = message.lower()
    for topic, data in FAQ_DATABASE.items():
        for keyword in data["keywords"]:
            if keyword in message_lower:
                return data["response"]
    return None


async def get_ai_response(message: str, session_id: str) -> str:
    if not EMERGENT_LLM_KEY:
        return "Je suis désolé, le service IA n'est pas disponible actuellement. Veuillez consulter nos ressources ou me contacter directement."

    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=session_id,
            system_message="""Tu es l'assistant virtuel de Stratégie & Expertise Santé, un service français d'accompagnement pour les personnes confrontées à des maladies professionnelles, accidents du travail, expertises médicales et litiges avec les assurances.

Ton rôle est d'aider les visiteurs à comprendre leurs droits et les orienter vers les bonnes ressources.

Règles importantes :
- Réponds toujours en français
- Sois empathique et rassurant
- Utilise un langage simple, sans jargon excessif
- Ne donne jamais de conseils médicaux ou juridiques spécifiques
- Oriente vers les professionnels compétents quand nécessaire
- Suggère de prendre contact pour un accompagnement personnalisé
- Sois concis mais complet

Pages du site à suggérer si pertinent :
- /expertise-medicale : Préparation aux expertises
- /accident-travail-maladie-professionnelle : Droits AT/MP
- /mdph : Démarches MDPH
- /protection-juridique : Protection juridique
- /tarifs : Nos tarifs
- /contact : Formulaire de contact
- /ressources : FAQ et glossaire"""
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")

        user_message = UserMessage(text=message)
        response = await chat.send_message(user_message)
        return response

    except Exception as e:
        logger.error(f"Error getting AI response: {str(e)}")
        return "Je suis désolé, une erreur s'est produite. Veuillez réessayer ou consulter nos ressources directement sur le site."
