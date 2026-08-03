import os
import uuid
import shutil
import asyncio
import base64
from datetime import datetime, timezone
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from config import logger, db

router = APIRouter(prefix="/upload", tags=["upload"])


def _store_files_to_object_storage(assembled_files, source="upload", user_email="", dossier_id=""):
    """Upload assembled files to Object Storage, save metadata to MongoDB."""
    stored = []
    try:
        from utils.storage import upload_file
    except Exception as e:
        logger.warning(f"Object storage not available for file persistence: {e}")
        return stored

    for file_info in assembled_files:
        name = file_info.get("name", "unknown")
        data_b64 = file_info.get("data", "")
        file_type = file_info.get("type", "application/octet-stream")
        if not data_b64:
            continue
        try:
            raw_bytes = base64.b64decode(data_b64)
            result = upload_file("dossier-originals", name, raw_bytes, file_type)
            doc_id = str(uuid.uuid4())
            result["file_id"] = doc_id

            # Persist metadata to MongoDB (sync via event loop)
            import asyncio
            doc_meta = {
                "id": doc_id,
                "original_filename": name,
                "content_type": file_type,
                "size": len(raw_bytes),
                "storage_path": result.get("storage_path", ""),
                "source": source,
                "user_email": user_email,
                "dossier_id": dossier_id,
                "status": "stored",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.ensure_future(db.documents.insert_one(doc_meta))
                else:
                    loop.run_until_complete(db.documents.insert_one(doc_meta))
            except Exception:
                pass

            stored.append(result)
        except Exception as e:
            logger.warning(f"Failed to store original file {name}: {e}")
    return stored

UPLOAD_DIR = "/tmp/chunked_uploads"
CHUNK_SIZE = 2 * 1024 * 1024  # 2 MB
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
MAX_TOTAL_SIZE = 100 * 1024 * 1024  # 100 MB


# ===================================================================
# MongoDB-backed chunk storage (multi-replica safe — fix 04/08/2026)
# ===================================================================
# La production tourne en multi-replicas : les chunks stockés sur le disque
# local d'un pod ne sont pas visibles des autres pods (upload → pod A,
# extract → pod B → "Upload non trouve"). Les chunks vivent désormais dans
# MongoDB (collection `upload_chunks`, TTL 1h), partagée par tous les pods.

_UPLOAD_CHUNK_INDEX_DONE = False


def _safe_filename(filename: str) -> str:
    return "".join(c for c in filename if c.isalnum() or c in ".-_")[:80]


async def _ensure_upload_chunk_indexes():
    global _UPLOAD_CHUNK_INDEX_DONE
    if _UPLOAD_CHUNK_INDEX_DONE:
        return
    try:
        await db.upload_chunks.create_index("created_at_dt", expireAfterSeconds=3600)
        await db.upload_chunks.create_index(
            [("upload_id", 1), ("safe_name", 1), ("chunk_index", 1)], unique=True
        )
        _UPLOAD_CHUNK_INDEX_DONE = True
    except Exception as e:
        logger.warning(f"upload_chunks index init failed: {e}")


# ===================================================================
# MongoDB-backed extraction state (resilient to process restarts/OOM)
# ===================================================================
# Replaces the previous in-memory `_extraction_results` dict so that if the
# server restarts mid-extraction (e.g. OOM on the 512MB Starter tier), the
# polling endpoint can still recover the state instead of returning 404.
#
# Collection: `extraction_results`
#   { id: "<uuid>", status, progress?, result?, stored_files?, error?, updated_at, created_at_dt }
# A TTL index on `created_at_dt` (1h) auto-cleans abandoned entries.

_EXTRACTION_TTL_INIT_DONE = False


async def _ensure_extraction_ttl():
    global _EXTRACTION_TTL_INIT_DONE
    if _EXTRACTION_TTL_INIT_DONE:
        return
    try:
        await db.extraction_results.create_index(
            "created_at_dt",
            expireAfterSeconds=3600,  # 1h
        )
        _EXTRACTION_TTL_INIT_DONE = True
    except Exception as e:
        logger.warning(f"extraction_results TTL index init failed: {e}")


async def _set_extraction(eid: str, state: dict):
    """Persist extraction state to MongoDB."""
    await _ensure_extraction_ttl()
    doc = {
        "id": eid,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        **{k: v for k, v in state.items() if k != "id"},
    }
    await db.extraction_results.update_one(
        {"id": eid},
        {"$set": doc, "$setOnInsert": {"created_at_dt": datetime.now(timezone.utc)}},
        upsert=True,
    )


async def _get_extraction(eid: str):
    return await db.extraction_results.find_one({"id": eid}, {"_id": 0, "created_at_dt": 0})


async def _delete_extraction(eid: str):
    try:
        await db.extraction_results.delete_one({"id": eid})
    except Exception:
        pass


# Legacy alias kept for backwards compatibility with any external import path.
# All real reads/writes now go through the async helpers above.
_extraction_results = {}


def _get_upload_dir(upload_id: str, filename: str) -> str:
    safe_name = _safe_filename(filename)
    path = os.path.join(UPLOAD_DIR, upload_id, safe_name)
    os.makedirs(path, exist_ok=True)
    return path


@router.post("/chunk")
async def upload_chunk(
    upload_id: str = Form(...),
    filename: str = Form(...),
    chunk_index: int = Form(...),
    total_chunks: int = Form(...),
    chunk: UploadFile = File(...)
):
    """Receive a single chunk of a large file upload (stored in MongoDB, multi-replica safe)."""
    if total_chunks > 500:
        raise HTTPException(400, "Trop de chunks")

    content = await chunk.read()

    if len(content) > CHUNK_SIZE + 1024:
        raise HTTPException(400, "Chunk trop volumineux")

    from bson import Binary
    await _ensure_upload_chunk_indexes()
    safe_name = _safe_filename(filename)
    await db.upload_chunks.update_one(
        {"upload_id": upload_id, "safe_name": safe_name, "chunk_index": chunk_index},
        {
            "$set": {"data": Binary(content), "total_chunks": total_chunks},
            "$setOnInsert": {"created_at_dt": datetime.now(timezone.utc)},
        },
        upsert=True,
    )

    received = await db.upload_chunks.count_documents(
        {"upload_id": upload_id, "safe_name": safe_name}
    )
    return {
        "status": "ok",
        "chunk_index": chunk_index,
        "received": received,
        "total": total_chunks,
        "complete": received >= total_chunks,
    }


async def _reassemble_files(upload_id, files_meta):
    """Reassemble chunked files (from MongoDB) into base64 payloads for the OCR pipeline."""
    assembled = []
    total_size = 0

    for meta in files_meta[:10]:
        filename = meta.get("name", "")
        total_chunks = meta.get("total_chunks", 0)
        file_type = meta.get("type", "")
        chunked = meta.get("chunked", False)

        if chunked:
            safe_name = _safe_filename(filename)
            docs = await db.upload_chunks.find(
                {"upload_id": upload_id, "safe_name": safe_name},
                {"_id": 0, "chunk_index": 1, "data": 1},
            ).sort("chunk_index", 1).to_list(600)

            if len(docs) < total_chunks:
                logger.warning(f"Upload {upload_id}/{safe_name}: {len(docs)}/{total_chunks} chunks trouves")
                assembled.append({"name": filename, "type": file_type, "data": ""})
                continue

            file_bytes = b"".join(bytes(d["data"]) for d in docs)

            if len(file_bytes) > MAX_FILE_SIZE:
                assembled.append({"name": filename, "type": file_type, "data": "", "status": "too_large"})
                continue

            total_size += len(file_bytes)
            if total_size > MAX_TOTAL_SIZE:
                assembled.append({"name": filename, "type": file_type, "data": "", "status": "total_exceeded"})
                continue

            encoded = base64.b64encode(file_bytes).decode()
            assembled.append({"name": filename, "type": file_type, "data": encoded})
        else:
            assembled.append({"name": filename, "type": file_type, "data": meta.get("data", "")})

    # Cleanup chunks (all replicas share MongoDB)
    try:
        await db.upload_chunks.delete_many({"upload_id": upload_id})
    except Exception:
        pass

    return assembled


async def _run_extraction(extraction_id, assembled_files):
    """Background task: run OCR extraction and store result in MongoDB."""
    try:
        prev = await _get_extraction(extraction_id) or {}
        stored = prev.get("stored_files", [])
        await _set_extraction(extraction_id, {
            "status": "processing",
            "progress": "Extraction OCR en cours...",
            "stored_files": stored,
        })

        from routes.dossier_express import _process_files_payload

        result = await _process_files_payload(assembled_files)
        await _set_extraction(extraction_id, {
            "status": "done",
            "result": result,
            "stored_files": stored,
        })
    except Exception as e:
        logger.error(f"Async extraction {extraction_id} failed: {e}", exc_info=True)
        try:
            await _set_extraction(extraction_id, {"status": "error", "error": str(e)[:500]})
        except Exception:
            pass


@router.post("/extract")
async def extract_chunked_files(request_body: dict):
    """Reassemble chunked files and extract text.

    TOUJOURS asynchrone : le gateway de production coupe les requetes a ~30s,
    or l'extraction Gemini d'un PDF scanne prend 60-150s. Le frontend
    poll /api/upload/extract-status/{id} (supporte deja ce mode).
    """
    upload_id = request_body.get("upload_id", "")
    files_meta = request_body.get("files", [])

    if not upload_id or not files_meta:
        raise HTTPException(status_code=400, detail="upload_id et files requis")

    has_inline = any(f.get("data") for f in files_meta)
    has_chunks = await db.upload_chunks.count_documents({"upload_id": upload_id}) > 0
    if not has_inline and not has_chunks:
        raise HTTPException(status_code=404, detail="Upload non trouve")

    assembled_files = await _reassemble_files(upload_id, files_meta)

    # Store original files to Object Storage (non-blocking best-effort)
    stored_files = await asyncio.to_thread(_store_files_to_object_storage, assembled_files)

    pdf_count = sum(
        1 for f in assembled_files
        if f.get("type") == "application/pdf" or f.get("name", "").lower().endswith(".pdf")
    )
    total_data = sum(len(f.get("data", "")) for f in assembled_files)
    estimated_raw = int(total_data * 0.75)

    extraction_id = str(uuid.uuid4())
    await _set_extraction(extraction_id, {"status": "queued", "stored_files": stored_files})
    asyncio.create_task(_run_extraction(extraction_id, assembled_files))
    return {"async": True, "extraction_id": extraction_id, "stored_files": stored_files, "message": f"Extraction en cours — {pdf_count} PDF(s), {estimated_raw/1024/1024:.1f} MB"}


@router.get("/extract-status/{extraction_id}")
async def get_extraction_status(extraction_id: str):
    """Poll for async extraction result. Backed by MongoDB so survives server restarts."""
    data = await _get_extraction(extraction_id)
    if not data:
        raise HTTPException(404, "Extraction non trouvee")

    status = data.get("status")
    if status == "done":
        result = data.get("result") or {}
        stored = data.get("stored_files", [])
        await _delete_extraction(extraction_id)
        return {"status": "done", "stored_files": stored, **result}
    elif status == "error":
        error = data.get("error", "Erreur inconnue")
        await _delete_extraction(extraction_id)
        return {"status": "error", "error": error}
    else:
        return {"status": status, "progress": data.get("progress", "")}
