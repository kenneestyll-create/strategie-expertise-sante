"""One-shot migration: link orphan documents (dossier_id='') to their dossier_express owner.

Strategy: for each document with dossier_id='' or missing, find the matching
dossier_express by `created_at` proximity (±2h) and `original_filename` match
inside `document_details` OR by `user_email` if dossier has that email.

Idempotent: tracks executed migration in `seo_migrations` collection (reuse infra)
under id `2026-05-18-link-orphan-documents`.

⚠️ Read-only by default. Set DRY_RUN=False to apply changes.
Run via: python -m scripts.migrate_link_orphan_documents

Backend / admin only. No public impact.
"""
import asyncio
import os
import sys
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# Allow running from /app/backend or from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv('/app/backend/.env')

from motor.motor_asyncio import AsyncIOMotorClient

DRY_RUN = os.environ.get("MIGRATION_DRY_RUN", "true").lower() in ("1", "true", "yes")
MIGRATION_ID = "2026-05-18-link-orphan-documents"


async def main():
    client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    db = client[os.environ["DB_NAME"]]

    # Idempotence check
    already = await db.seo_migrations.find_one({"id": MIGRATION_ID}, {"_id": 0, "id": 1})
    if already and not DRY_RUN:
        print(f"⏭️  Migration {MIGRATION_ID} already applied. Skipping.")
        return

    # Load all dossier_express records (for matching)
    dossiers = []
    async for d in db.dossier_express.find({}, {"_id": 0, "id": 1, "email": 1, "created_at": 1, "document_details": 1, "original_documents": 1}):
        dossiers.append(d)
    print(f"📋 Loaded {len(dossiers)} dossier_express records")

    # Iterate orphan documents
    query_orphan = {"$or": [{"dossier_id": ""}, {"dossier_id": None}, {"dossier_id": {"$exists": False}}]}
    total_orphans = await db.documents.count_documents(query_orphan)
    print(f"🔍 Found {total_orphans} orphan document(s)\n")

    matched = 0
    unmatched = 0
    matches_log = []

    async for doc in db.documents.find(query_orphan, {"_id": 0}):
        doc_id = doc.get("id")
        fname = doc.get("original_filename", "")
        sp = doc.get("storage_path", "")
        doc_created = doc.get("created_at", "")
        # Parse doc time
        try:
            doc_dt = datetime.fromisoformat(doc_created.replace("Z", "+00:00")) if doc_created else None
        except Exception:
            doc_dt = None

        best_match = None
        best_match_reason = ""

        # 1) Exact match via storage_path in dossier.original_documents
        for d in dossiers:
            for od in (d.get("original_documents") or []):
                if isinstance(od, dict) and (od.get("storage_path") == sp or od.get("file_id") == doc_id):
                    best_match = d
                    best_match_reason = "storage_path/file_id match"
                    break
            if best_match:
                break

        # 2) Match via filename in document_details + temporal proximity (±2h)
        if not best_match and doc_dt:
            for d in dossiers:
                try:
                    d_dt = datetime.fromisoformat(d["created_at"].replace("Z", "+00:00"))
                except Exception:
                    continue
                if abs((d_dt - doc_dt).total_seconds()) > 7200:  # 2h
                    continue
                for dd in (d.get("document_details") or []):
                    if isinstance(dd, dict) and dd.get("name") == fname:
                        best_match = d
                        best_match_reason = f"filename+time (±{abs((d_dt-doc_dt).total_seconds())/60:.0f}min)"
                        break
                if best_match:
                    break

        if best_match:
            matched += 1
            matches_log.append((doc_id[:12], fname[:40], best_match["id"], best_match_reason))
            if not DRY_RUN:
                await db.documents.update_one(
                    {"id": doc_id},
                    {"$set": {"dossier_id": best_match["id"], "user_email": best_match.get("email", "")}}
                )
        else:
            unmatched += 1

    print(f"\n✅ Matched: {matched}")
    print(f"❌ Unmatched: {unmatched}")
    if matches_log:
        print("\nMatches detail (first 20):")
        for m in matches_log[:20]:
            print(f"  {m[0]}  {m[1]:<40}  → {m[2]}  ({m[3]})")

    if not DRY_RUN:
        await db.seo_migrations.insert_one({
            "id": MIGRATION_ID,
            "description": "Link orphan documents (dossier_id='') to their dossier_express owner via storage_path + filename+temporal match",
            "applied_at": datetime.now(timezone.utc).isoformat(),
            "matched_count": matched,
            "unmatched_count": unmatched,
        })
        print(f"\n📝 Migration {MIGRATION_ID} recorded in seo_migrations")
    else:
        print("\n💡 DRY RUN — no changes applied. Set MIGRATION_DRY_RUN=false to execute.")


if __name__ == "__main__":
    asyncio.run(main())
