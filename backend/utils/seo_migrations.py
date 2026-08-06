"""SEO title/description migrations — idempotent.

Each migration has a unique ID. On boot, we check the `seo_migrations` collection.
If the migration ID has already been applied (=> a doc with that id exists), we skip.
Otherwise we apply the update_one operations and persist a marker.

This is the safe way to propagate optimized titles/meta_descriptions to production
without overwriting analytics or any unrelated fields, and without re-running the
full seed (which would replace fields). Adding a new migration = appending a dict
to MIGRATIONS list below.
"""
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


# Each migration is a list of {"slug": ..., "title": ..., "meta_description": ...}
MIGRATIONS = [
    {
        "id": "2026-05-17-quick-wins-vague2",
        "description": "SEO Quick Wins Vague 2 — titles + meta descriptions optimisés sur 3 pages /guide/* (faute inexcusable, AT non déclaré, délai prescription MP)",
        "updates": [
            {
                "slug": "accident-travail-non-declare-employeur",
                "title": "Accident du Travail Non Déclaré par l'Employeur : Vos Recours",
                "meta_description": "Employeur qui refuse la déclaration AT ? Procédure CPAM, sanctions employeur, mise en demeure. Délai 2 ans pour faire valoir vos droits.",
            },
            {
                "slug": "faute-inexcusable-employeur",
                "title": "Faute Inexcusable de l'Employeur : Conditions + Indemnités",
                "meta_description": "Faute inexcusable : 3 conditions à prouver, indemnisation complémentaire CPAM + employeur. Délai 2 ans. Guide étape par étape pour saisir le pôle social.",
            },
            {
                "slug": "delai-prescription-maladie-professionnelle",
                "title": "Délai de Prescription Maladie Professionnelle CPAM",
                "meta_description": "Combien de temps pour déclarer une maladie professionnelle ? Délais CPAM (2 ans), prescription civile (5 ans), cas particuliers et erreurs à éviter.",
            },
        ],
    },
    {
        "id": "2026-08-06-phase1-maillage-guides",
        "description": "Phase 1 SEO — Maillage interne des 17 guides (cocons sémantiques). Cibles gelées exclues (/expertise-medicale, /expertise-medicale/assureur, /dossier-express) jusqu'à J+28.",
        "updates": [
            {"slug": "refus-mdph-aah-que-faire", "content.maillage": [
                {"slug": "refus-aah-rsdae-non-reconnue", "text": "Refus AAH pour RSDAE non reconnue : la stratégie de recours"},
                {"slug": "comment-demander-rqth-strategic", "text": "Demander la RQTH : démarches et stratégie complètes"},
                {"slug": "recours-tribunal-judiciaire-pole-social", "text": "Saisir le pôle social du tribunal judiciaire après un refus"},
                {"href": "/mdph", "text": "MDPH : comprendre vos droits et structurer votre dossier"},
                {"href": "/calculatrice-aah", "text": "Simulateur AAH : estimez le montant de vos droits"},
            ]},
            {"slug": "taux-ipp-5-pourcent-contester", "content.maillage": [
                {"slug": "rente-accident-travail-calcul-contestation", "text": "Rente accident du travail : calcul, montant et contestation"},
                {"slug": "ipp-fonction-publique-hospitaliere", "text": "IPP fonction publique hospitalière : ATI et recours"},
                {"slug": "expertise-medicale-defavorable-recours", "text": "Expertise médicale défavorable : les recours possibles"},
                {"href": "/calculatrice-ipp", "text": "Simulateur rente IPP : calculez votre indemnisation"},
            ]},
            {"slug": "expertise-medicale-defavorable-recours", "content.maillage": [
                {"slug": "comment-preparer-expertise-medicale", "text": "Bien préparer son expertise médicale : le guide complet"},
                {"slug": "taux-ipp-5-pourcent-contester", "text": "Contester un taux IPP trop bas après l'expertise"},
                {"slug": "recours-tribunal-judiciaire-pole-social", "text": "Le recours devant le pôle social du tribunal judiciaire"},
                {"href": "/medecin-conseil", "text": "Médecin conseil CPAM : rôle, convocation et contestation"},
            ]},
            {"slug": "accident-travail-non-declare-employeur", "content.maillage": [
                {"slug": "faute-inexcusable-employeur", "text": "Faute inexcusable de l'employeur : conditions et indemnités"},
                {"slug": "rente-accident-travail-calcul-contestation", "text": "Rente accident du travail : calcul et contestation"},
                {"slug": "recours-tribunal-judiciaire-pole-social", "text": "Saisir le pôle social du tribunal judiciaire"},
                {"href": "/accident-travail-maladie-professionnelle", "text": "Accident du travail et maladie professionnelle : vos droits et recours"},
            ]},
            {"slug": "refus-maladie-professionnelle-cpam-recours", "content.maillage": [
                {"slug": "comment-faire-reconnaitre-maladie-professionnelle", "text": "Faire reconnaître une maladie professionnelle : les étapes"},
                {"slug": "delai-prescription-maladie-professionnelle", "text": "Délai de prescription maladie professionnelle : ne perdez pas vos droits"},
                {"slug": "recours-tribunal-judiciaire-pole-social", "text": "Contester devant le pôle social du tribunal judiciaire"},
                {"href": "/accident-travail-maladie-professionnelle", "text": "Accident du travail et maladie professionnelle : vos droits et recours"},
            ]},
            {"slug": "faute-inexcusable-employeur", "content.maillage": [
                {"slug": "accident-travail-non-declare-employeur", "text": "Accident du travail non déclaré par l'employeur : vos recours"},
                {"slug": "rente-accident-travail-calcul-contestation", "text": "Rente accident du travail : calcul de l'indemnisation"},
                {"slug": "recours-tribunal-judiciaire-pole-social", "text": "La procédure devant le pôle social du tribunal judiciaire"},
                {"href": "/accident-travail-maladie-professionnelle", "text": "Accident du travail et maladie professionnelle : vos droits et recours"},
                {"href": "/calculatrice-ipp", "text": "Simulateur rente IPP : estimez l'indemnisation complémentaire"},
            ]},
            {"slug": "inaptitude-travail-droits-recours", "content.maillage": [
                {"slug": "refus-maladie-professionnelle-cpam-recours", "text": "Refus de maladie professionnelle par la CPAM : les recours"},
                {"slug": "comment-demander-rqth-strategic", "text": "Demander la RQTH après une inaptitude"},
                {"href": "/accident-travail-maladie-professionnelle", "text": "Accident du travail et maladie professionnelle : vos droits"},
                {"href": "/mdph", "text": "MDPH : structurer votre dossier de compensation"},
            ]},
            {"slug": "rente-accident-travail-calcul-contestation", "content.maillage": [
                {"slug": "taux-ipp-5-pourcent-contester", "text": "Taux IPP de 5 % : comment le contester"},
                {"slug": "faute-inexcusable-employeur", "text": "Faute inexcusable : obtenir une indemnisation complémentaire"},
                {"href": "/calculatrice-ipp", "text": "Simulateur rente IPP : calculez votre rente en ligne"},
                {"href": "/accident-travail-maladie-professionnelle", "text": "Accident du travail et maladie professionnelle : vos droits et recours"},
            ]},
            {"slug": "recours-tribunal-judiciaire-pole-social", "content.maillage": [
                {"slug": "refus-maladie-professionnelle-cpam-recours", "text": "Refus de maladie professionnelle CPAM : préparer le recours"},
                {"slug": "refus-mdph-aah-que-faire", "text": "Refus MDPH ou AAH : les recours possibles"},
                {"slug": "expertise-medicale-defavorable-recours", "text": "Expertise médicale défavorable : contester les conclusions"},
                {"slug": "faute-inexcusable-employeur", "text": "Faute inexcusable de l'employeur : saisir le pôle social"},
                {"href": "/accident-travail-maladie-professionnelle", "text": "Accident du travail et maladie professionnelle : vos droits et recours"},
                {"href": "/mdph", "text": "MDPH : comprendre vos droits avant le contentieux"},
            ]},
            {"slug": "delai-prescription-maladie-professionnelle", "content.maillage": [
                {"slug": "comment-faire-reconnaitre-maladie-professionnelle", "text": "Faire reconnaître une maladie professionnelle : la procédure"},
                {"slug": "refus-maladie-professionnelle-cpam-recours", "text": "Refus CPAM : les recours contre une décision défavorable"},
                {"href": "/accident-travail-maladie-professionnelle", "text": "Accident du travail et maladie professionnelle : vos droits et recours"},
            ]},
            {"slug": "comment-preparer-expertise-medicale", "content.maillage": [
                {"slug": "expertise-medicale-defavorable-recours", "text": "Expertise médicale défavorable : les recours après coup"},
                {"slug": "taux-ipp-5-pourcent-contester", "text": "Contester le taux IPP fixé après l'expertise"},
                {"href": "/medecin-conseil", "text": "Médecin conseil CPAM : rôle, convocation et contestation"},
                {"href": "/calculatrice-ipp", "text": "Simulateur IPP : anticipez l'enjeu financier de l'expertise"},
            ]},
            {"slug": "comment-demander-rqth-strategic", "content.maillage": [
                {"slug": "refus-mdph-aah-que-faire", "text": "Refus MDPH / AAH : que faire en cas de rejet"},
                {"slug": "refus-aah-rsdae-non-reconnue", "text": "RSDAE non reconnue : la stratégie de recours AAH"},
                {"href": "/mdph", "text": "MDPH : comprendre vos droits et monter votre dossier"},
                {"href": "/calculatrice-aah", "text": "Simulateur AAH : vérifiez votre éligibilité"},
            ]},
            {"slug": "comment-faire-reconnaitre-maladie-professionnelle", "content.maillage": [
                {"slug": "delai-prescription-maladie-professionnelle", "text": "Délais de prescription : déclarez votre maladie professionnelle à temps"},
                {"slug": "refus-maladie-professionnelle-cpam-recours", "text": "Refus de la CPAM : les recours qui fonctionnent"},
                {"slug": "maladie-professionnelle-definition-droits", "text": "Maladie professionnelle : définition et droits ouverts"},
                {"href": "/accident-travail-maladie-professionnelle", "text": "Accident du travail et maladie professionnelle : vos droits et recours"},
            ]},
            {"slug": "maladie-professionnelle-definition-droits", "content.maillage": [
                {"slug": "comment-faire-reconnaitre-maladie-professionnelle", "text": "Faire reconnaître votre maladie professionnelle : les étapes"},
                {"slug": "refus-maladie-professionnelle-cpam-recours", "text": "Refus maladie professionnelle CPAM : recours et délais"},
                {"href": "/accident-travail-maladie-professionnelle", "text": "Accident du travail et maladie professionnelle : vos droits et recours"},
            ]},
            {"slug": "ptia-definition-droits-strategie", "content.maillage": [
                {"slug": "comment-preparer-expertise-medicale", "text": "Préparer l'expertise médicale demandée par l'assureur"},
                {"slug": "expertise-medicale-defavorable-recours", "text": "Expertise défavorable : contester les conclusions"},
                {"href": "/protection-juridique", "text": "Protection juridique : faire valoir vos droits face à l'assureur"},
            ]},
            {"slug": "refus-aah-rsdae-non-reconnue", "content.maillage": [
                {"slug": "refus-mdph-aah-que-faire", "text": "Refus MDPH AAH : recours, délais et solutions"},
                {"slug": "comment-demander-rqth-strategic", "text": "Demander la RQTH en parallèle de l'AAH"},
                {"slug": "recours-tribunal-judiciaire-pole-social", "text": "Saisir le pôle social après un refus définitif"},
                {"href": "/mdph", "text": "MDPH : structurer un dossier solide"},
                {"href": "/calculatrice-aah", "text": "Simulateur AAH : estimez vos droits"},
            ]},
            {"slug": "ipp-fonction-publique-hospitaliere", "content.maillage": [
                {"slug": "taux-ipp-5-pourcent-contester", "text": "Contester un taux IPP trop bas"},
                {"slug": "rente-accident-travail-calcul-contestation", "text": "Rente accident du travail : calcul et contestation"},
                {"href": "/calculatrice-ipp", "text": "Simulateur rente IPP : calculez votre indemnisation"},
            ]},
        ],
    },
]


async def apply_pending_migrations(db) -> dict:
    """Run any migration whose id is not yet recorded in `seo_migrations`.

    Returns a small report: {applied: [...], skipped: [...], errors: [...]}
    """
    report = {"applied": [], "skipped": [], "errors": []}
    for migration in MIGRATIONS:
        mid = migration["id"]
        existing = await db.seo_migrations.find_one({"id": mid}, {"_id": 0, "id": 1})
        if existing:
            report["skipped"].append(mid)
            continue
        try:
            modified = 0
            for upd in migration["updates"]:
                slug = upd["slug"]
                set_fields = {k: v for k, v in upd.items() if k != "slug"}
                res = await db.seo_pages.update_one({"slug": slug}, {"$set": set_fields})
                modified += res.modified_count
            await db.seo_migrations.insert_one({
                "id": mid,
                "description": migration.get("description", ""),
                "applied_at": datetime.now(timezone.utc).isoformat(),
                "updates_count": len(migration["updates"]),
                "modified_count": modified,
            })
            report["applied"].append({"id": mid, "modified": modified, "total_updates": len(migration["updates"])})
            logger.info(f"SEO migration applied: {mid} → {modified}/{len(migration['updates'])} pages modified")
        except Exception as e:
            report["errors"].append({"id": mid, "error": str(e)})
            logger.error(f"SEO migration {mid} failed: {e}")
    return report
