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
    safe_name = "".join(c for c in filename if c.isalnum() or c in ".-_")[:80]
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
    """Receive a single chunk of a large file upload."""
    if total_chunks > 500:
        raise HTTPException(400, "Trop de chunks")

    upload_dir = _get_upload_dir(upload_id, filename)
    chunk_path = os.path.join(upload_dir, f"chunk_{chunk_index:04d}")
    content = await chunk.read()

    if len(content) > CHUNK_SIZE + 1024:
        raise HTTPException(400, "Chunk trop volumineux")

    with open(chunk_path, "wb") as f:
        f.write(content)

    received = len([n for n in os.listdir(upload_dir) if n.startswith("chunk_")])
    return {
        "status": "ok",
        "chunk_index": chunk_index,
        "received": received,
        "total": total_chunks,
        "complete": received >= total_chunks,
    }


def _reassemble_files(upload_id, files_meta):
    """Reassemble chunked files into base64 payloads for the OCR pipeline."""
    upload_path = os.path.join(UPLOAD_DIR, upload_id)
    assembled = []
    total_size = 0

    for meta in files_meta[:10]:
        filename = meta.get("name", "")
        total_chunks = meta.get("total_chunks", 0)
        file_type = meta.get("type", "")
        chunked = meta.get("chunked", False)

        if chunked:
            safe_name = "".join(c for c in filename if c.isalnum() or c in ".-_")[:80]
            file_dir = os.path.join(upload_path, safe_name)
            if not os.path.isdir(file_dir):
                assembled.append({"name": filename, "type": file_type, "data": ""})
                continue

            chunk_files = sorted([f for f in os.listdir(file_dir) if f.startswith("chunk_")])
            if len(chunk_files) < total_chunks:
                assembled.append({"name": filename, "type": file_type, "data": ""})
                continue

            file_bytes = bytearray()
            for cf in chunk_files:
                with open(os.path.join(file_dir, cf), "rb") as f:
                    file_bytes.extend(f.read())

            if len(file_bytes) > MAX_FILE_SIZE:
                assembled.append({"name": filename, "type": file_type, "data": "", "status": "too_large"})
                continue

            total_size += len(file_bytes)
            if total_size > MAX_TOTAL_SIZE:
                assembled.append({"name": filename, "type": file_type, "data": "", "status": "total_exceeded"})
                continue

            encoded = base64.b64encode(bytes(file_bytes)).decode()
            assembled.append({"name": filename, "type": file_type, "data": encoded})
        else:
            assembled.append({"name": filename, "type": file_type, "data": meta.get("data", "")})

    # Cleanup upload directory
    try:
        shutil.rmtree(upload_path, ignore_errors=True)
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
    """Reassemble chunked files and extract text. For large files, returns immediately with a poll ID."""
    upload_id = request_body.get("upload_id", "")
    files_meta = request_body.get("files", [])

    if not upload_id or not files_meta:
        raise HTTPException(status_code=400, detail="upload_id et files requis")

    upload_path = os.path.join(UPLOAD_DIR, upload_id)
    if not os.path.isdir(upload_path):
        raise HTTPException(status_code=404, detail="Upload non trouve")

    assembled_files = _reassemble_files(upload_id, files_meta)

    # Store original files to Object Storage (non-blocking best-effort)
    stored_files = await asyncio.to_thread(_store_files_to_object_storage, assembled_files)

    # Calculate total data size and PDF count
    total_data = sum(len(f.get("data", "")) for f in assembled_files)
    pdf_count = sum(
        1 for f in assembled_files
        if f.get("type") == "application/pdf" or f.get("name", "").lower().endswith(".pdf")
    )

    # Heuristic ALIGNED with /api/extract-document-text: > 2 PDFs OR > 5 MB raw → async
    # (avoids ingress proxy timeouts ~120s when multiple scanned PDFs hit Gemini)
    HEAVY_PDF_COUNT = 2
    HEAVY_RAW_BYTES = 5 * 1024 * 1024  # 5 MB raw decoded — same as extract-document-text
    # base64 size ≈ 4/3 of decoded; total_data is base64 length here
    estimated_raw = int(total_data * 0.75)
    if pdf_count > HEAVY_PDF_COUNT or estimated_raw > HEAVY_RAW_BYTES:
        extraction_id = str(uuid.uuid4())
        await _set_extraction(extraction_id, {"status": "queued", "stored_files": stored_files})
        asyncio.create_task(_run_extraction(extraction_id, assembled_files))
        return {"async": True, "extraction_id": extraction_id, "stored_files": stored_files, "message": f"Extraction en cours — {pdf_count} PDF(s), {estimated_raw/1024/1024:.1f} MB"}

    # For smaller payloads, process synchronously (faster)
    from routes.dossier_express import _process_files_payload

    result = await _process_files_payload(assembled_files)
    result["stored_files"] = stored_files
    return result


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
