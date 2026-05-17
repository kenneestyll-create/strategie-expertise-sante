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
