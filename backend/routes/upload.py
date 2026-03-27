import os
import uuid
import shutil
from datetime import datetime, timezone
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from config import logger

router = APIRouter(prefix="/upload", tags=["upload"])

UPLOAD_DIR = "/tmp/chunked_uploads"
CHUNK_SIZE = 2 * 1024 * 1024  # 2 MB
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
MAX_TOTAL_SIZE = 100 * 1024 * 1024  # 100 MB


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
    chunk: UploadFile = File(...),
):
    """Receive a single chunk of a file. Client splits large files into ~2MB chunks."""
    if total_chunks > 100:
        raise HTTPException(status_code=400, detail="Trop de chunks")

    file_dir = _get_upload_dir(upload_id, filename)
    chunk_path = os.path.join(file_dir, f"chunk_{chunk_index:04d}")

    data = await chunk.read()
    if len(data) > CHUNK_SIZE + 1024:
        raise HTTPException(status_code=400, detail="Chunk trop volumineux")

    with open(chunk_path, "wb") as f:
        f.write(data)

    # Count received chunks
    received = len([n for n in os.listdir(file_dir) if n.startswith("chunk_")])

    return {
        "status": "ok",
        "chunk_index": chunk_index,
        "received": received,
        "total": total_chunks,
        "complete": received >= total_chunks,
    }


@router.post("/extract")
async def extract_chunked_files(request_body: dict):
    """Reassemble chunked files and extract text using the existing OCR pipeline."""
    upload_id = request_body.get("upload_id", "")
    files_meta = request_body.get("files", [])

    if not upload_id or not files_meta:
        raise HTTPException(status_code=400, detail="upload_id et files requis")

    upload_path = os.path.join(UPLOAD_DIR, upload_id)
    if not os.path.isdir(upload_path):
        raise HTTPException(status_code=404, detail="Upload non trouve")

    import base64
    from routes.strategiia import extract_document_text
    from fastapi import Request

    # Reassemble files and convert to base64 for the existing pipeline
    assembled_files = []
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
                assembled_files.append({"name": filename, "type": file_type, "data": ""})
                continue

            # Reassemble chunks in order
            chunk_files = sorted([f for f in os.listdir(file_dir) if f.startswith("chunk_")])
            if len(chunk_files) < total_chunks:
                assembled_files.append({"name": filename, "type": file_type, "data": ""})
                continue

            file_bytes = bytearray()
            for cf in chunk_files:
                with open(os.path.join(file_dir, cf), "rb") as f:
                    file_bytes.extend(f.read())

            if len(file_bytes) > MAX_FILE_SIZE:
                assembled_files.append({
                    "name": filename, "type": file_type, "data": "",
                    "status": "too_large", "method": "fichier trop volumineux"
                })
                continue

            total_size += len(file_bytes)
            if total_size > MAX_TOTAL_SIZE:
                assembled_files.append({
                    "name": filename, "type": file_type, "data": "",
                    "status": "total_exceeded"
                })
                continue

            encoded = base64.b64encode(bytes(file_bytes)).decode()
            assembled_files.append({"name": filename, "type": file_type, "data": encoded})
        else:
            # Non-chunked file data passed directly as base64
            assembled_files.append({
                "name": filename,
                "type": file_type,
                "data": meta.get("data", ""),
            })

    # Cleanup upload directory
    try:
        shutil.rmtree(upload_path, ignore_errors=True)
    except Exception:
        pass

    # Use the existing extraction pipeline via a mock request
    from starlette.requests import Request as StarletteRequest
    from starlette.datastructures import State

    class MockRequest:
        async def json(self):
            return {"files": assembled_files}

    mock_req = MockRequest()

    # Import and call the extraction logic directly
    from routes.strategiia import router as strat_router
    import importlib
    import routes.strategiia as strat_module

    # Call extract function directly
    result = await strat_module.extract_document_text(mock_req)
    return result
