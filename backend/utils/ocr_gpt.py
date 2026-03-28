import os
import json
import logging

import openai

logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

SYSTEM_PROMPT = """Tu es un expert en extraction de données à partir de documents administratifs français liés aux accidents du travail, maladies professionnelles, expertises médicales, MDPH et assurances.

À partir du texte OCR fourni, extrais les champs suivants en JSON :
{
  "dates": ["JJ/MM/AAAA"],
  "montants": ["montant€"],
  "references": ["REF-XXX"],
  "numero_ss": "numéro sécurité sociale",
  "noms": ["Nom Prénom"],
  "taux_ipp": [pourcentage entier],
  "type_dossier_detected": ["at", "mp", "mdph", "expertise", "ipp"],
  "organisme": "CPAM|CRAMIF|MSA|MDPH|CNSA|TASS|TCI",
  "resume": "résumé en 2-3 phrases du contenu du document",
  "recommandations": ["action recommandée pour le client"]
}

Règles :
- Retourne UNIQUEMENT du JSON valide, sans texte autour
- Si un champ n'est pas trouvé, utilise null ou un tableau vide
- Les dates doivent être au format JJ/MM/AAAA
- Les montants doivent inclure le symbole €
- Le numéro de sécurité sociale fait 13 chiffres + 2 clé
- type_dossier_detected peut contenir plusieurs types si le document concerne plusieurs domaines
"""


async def extract_fields_gpt4o(raw_text: str) -> dict:
    if not OPENAI_API_KEY:
        return {"error": "Clé OpenAI non configurée", "fields": {}, "enhanced": False}

    if not raw_text or len(raw_text.strip()) < 10:
        return {"fields": {}, "enhanced": False, "message": "Texte trop court pour l'analyse"}

    try:
        client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)

        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Extrais les champs du texte OCR suivant :\n\n{raw_text[:8000]}"},
            ],
            max_tokens=2000,
            temperature=0.1,
        )

        response_text = response.choices[0].message.content.strip()
        if response_text.startswith("```"):
            response_text = response_text.split("\n", 1)[1] if "\n" in response_text else response_text
            response_text = response_text.rsplit("```", 1)[0]

        fields = json.loads(response_text)
        return {"fields": fields, "source": "gpt-4o", "enhanced": True}

    except json.JSONDecodeError:
        logger.error("GPT-4o returned non-JSON response for OCR extraction")
        return {"fields": {}, "enhanced": False, "error": "Réponse IA non structurée"}
    except Exception as e:
        error_msg = str(e)
        logger.error(f"GPT-4o OCR extraction failed: {e}")
        return {"fields": {}, "enhanced": False, "error": f"Erreur IA: {error_msg}"}
