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

# In-memory store for async extraction results (cleared on completion)
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
    """Background task: run OCR extraction and store result."""
    try:
        stored = _extraction_results.get(extraction_id, {}).get("stored_files", [])
        _extraction_results[extraction_id] = {"status": "processing", "progress": "Extraction OCR en cours...", "stored_files": stored}

        import routes.dossier_express as dossier_module

        class MockRequest:
            async def json(self):
                return {"files": assembled_files}

        result = await dossier_module.extract_document_text(MockRequest())
        _extraction_results[extraction_id] = {"status": "done", "result": result, "stored_files": stored}
    except Exception as e:
        logger.error(f"Async extraction {extraction_id} failed: {e}")
        _extraction_results[extraction_id] = {"status": "error", "error": str(e)}


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

    # Calculate total data size
    total_data = sum(len(f.get("data", "")) for f in assembled_files)

    # For large payloads (> 15MB base64 ~ 10MB raw), process asynchronously
    if total_data > 15 * 1024 * 1024:
        extraction_id = str(uuid.uuid4())
        _extraction_results[extraction_id] = {"status": "queued", "stored_files": stored_files}
        asyncio.create_task(_run_extraction(extraction_id, assembled_files))
        return {"async": True, "extraction_id": extraction_id, "stored_files": stored_files, "message": "Extraction en cours — fichier volumineux"}

    # For smaller payloads, process synchronously (faster)
    import routes.dossier_express as dossier_module

    class MockRequest:
        async def json(self):
            return {"files": assembled_files}

    result = await dossier_module.extract_document_text(MockRequest())
    result["stored_files"] = stored_files
    return result


@router.get("/extract-status/{extraction_id}")
async def get_extraction_status(extraction_id: str):
    """Poll for async extraction result."""
    data = _extraction_results.get(extraction_id)
    if not data:
        raise HTTPException(404, "Extraction non trouvee")

    if data["status"] == "done":
        result = data["result"]
        stored = data.get("stored_files", [])
        del _extraction_results[extraction_id]
        return {"status": "done", "stored_files": stored, **result}
    elif data["status"] == "error":
        error = data.get("error", "Erreur inconnue")
        del _extraction_results[extraction_id]
        return {"status": "error", "error": error}
    else:
        return {"status": data["status"], "progress": data.get("progress", "")}
