"""Benchmark contrôlé Sonnet 4.5 vs Sonnet 5 — cas fictif Mme DEMONSTRATION Claire.
Lecture seule : ne modifie AUCUN fichier de l'application. Résultats dans /app/memory/benchmarks/.
"""
import asyncio, json, os, sys, time

sys.path.insert(0, "/app/backend")
from dotenv import load_dotenv
load_dotenv("/app/backend/.env")

OUT_DIR = "/app/memory/benchmarks/SONNET5_2026-09-06"
os.makedirs(OUT_DIR, exist_ok=True)

DEMO_DIR = "/app/frontend/public/cas-demonstration"
PDFS = [
    "1-certificat-medical-initial.pdf",
    "2-notification-refus-cpam.pdf",
    "3-compte-rendu-psychiatrique.pdf",
    "4-arret-travail-scan-degrade.pdf",
    "5-elements-contexte-professionnel.pdf",
    "6-courrier-medecin-conseil.pdf",
]

SITUATION = (
    "Je suis cadre de proximité dans un établissement médico-social depuis 2015. "
    "Depuis 2023, mes conditions de travail se sont fortement dégradées (sous-effectif permanent, "
    "injonctions contradictoires, astreintes doublées sans compensation, alerte écrite à la direction "
    "restée sans réponse). J'ai développé une dépression sévère constatée le 18/02/2026 et je suis en "
    "arrêt depuis. J'ai déclaré ma maladie en maladie professionnelle (hors tableau). La CPAM a refusé "
    "le 12/05/2026 : le médecin-conseil a évalué mon taux d'incapacité permanente prévisible à 20 %, "
    "sous le seuil de 25 %, donc mon dossier n'a même pas été transmis au CRRMP. Mon psychiatre estime "
    "pourtant que mon incapacité est durable et que l'origine professionnelle est prépondérante. "
    "Je veux contester ce refus et faire reconnaître ma maladie professionnelle. Que puis-je faire ?"
)

NAME = "Mme DEMONSTRATION Claire"
TYPE_DOSSIER = "maladie_professionnelle"
REGIME = "regime_general"

MODELS = {
    "sonnet_4_5": "claude-sonnet-4-5-20250929",
    "sonnet_5": "claude-sonnet-5",
}


async def extract_documents() -> str:
    from utils.document_extraction import extract_pdf_full_pipeline
    combined = ""
    details = []
    for fname in PDFS:
        path = os.path.join(DEMO_DIR, fname)
        with open(path, "rb") as f:
            data = f.read()
        text, method, pages, status = await extract_pdf_full_pipeline(data, fname)
        details.append({"file": fname, "method": method, "pages": pages, "status": status, "chars": len(text)})
        combined += f"\n\n=== DOCUMENT: {fname} ===\n{text if text else '[Contenu non extractible]'}"
        print(f"[EXTRACT] {fname} -> {status} ({len(text)} chars, {method})")
    with open(f"{OUT_DIR}/extraction_details.json", "w") as f:
        json.dump(details, f, ensure_ascii=False, indent=1)
    return combined.strip()


def build_prompts(documents_text: str):
    from constants.prompts import DOSSIER_EXPRESS_SYSTEM_PROMPT, DOSSIER_EXPRESS_PROMPT
    user_msg = f"""DOSSIER EXPRESS IA - Analyse complete demandee

Client : {NAME}
Type de dossier : {TYPE_DOSSIER}
Regime : {REGIME}

DESCRIPTION DE LA SITUATION :
{SITUATION}

CONTENU DES DOCUMENTS FOURNIS :
{documents_text[:120000]}

{DOSSIER_EXPRESS_PROMPT}"""
    return DOSSIER_EXPRESS_SYSTEM_PROMPT, user_msg


def run_model(model_id: str, system: str, user_msg: str) -> dict:
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"], timeout=300.0)
    t0 = time.monotonic()
    parts = []
    with client.messages.stream(
        model=model_id,
        max_tokens=8000,
        system=system,
        messages=[{"role": "user", "content": user_msg}],
    ) as stream:
        for chunk in stream.text_stream:
            parts.append(chunk)
        final = stream.get_final_message()
    elapsed = round(time.monotonic() - t0, 1)
    text = "".join(parts)
    usage = {"input_tokens": final.usage.input_tokens, "output_tokens": final.usage.output_tokens}
    return {"model": model_id, "elapsed_s": elapsed, "usage": usage, "chars": len(text), "text": text}


async def main():
    print("=== ÉTAPE 1 : extraction des 6 pièces (pipeline production) ===")
    documents_text = await extract_documents()
    print(f"[EXTRACT] total combiné : {len(documents_text)} chars")
    with open(f"{OUT_DIR}/documents_text.txt", "w") as f:
        f.write(documents_text)

    system, user_msg = build_prompts(documents_text)
    print(f"[PROMPT] system={len(system)} chars, user={len(user_msg)} chars")

    results = {}
    for label, model_id in MODELS.items():
        print(f"=== ÉTAPE 2 : génération {label} ({model_id}) ===")
        r = await asyncio.to_thread(run_model, model_id, system, user_msg)
        results[label] = {k: v for k, v in r.items() if k != "text"}
        with open(f"{OUT_DIR}/rapport_{label}.md", "w") as f:
            f.write(r["text"])
        print(f"[{label}] {r['elapsed_s']}s | in={r['usage']['input_tokens']} out={r['usage']['output_tokens']} | {r['chars']} chars")

    prices = {"sonnet_4_5": (3.0, 15.0), "sonnet_5": (2.0, 10.0)}
    for label, res in results.items():
        pin, pout = prices[label]
        u = res["usage"]
        res["cost_usd"] = round(u["input_tokens"] / 1e6 * pin + u["output_tokens"] / 1e6 * pout, 4)

    with open(f"{OUT_DIR}/metrics.json", "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    print("=== TERMINÉ ===")
    print(json.dumps(results, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    asyncio.run(main())
