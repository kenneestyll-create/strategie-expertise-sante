"""
Test suite for the BUG FIX (04/08/2026):
  1. Chunks are stored in MongoDB (collection `upload_chunks`) instead of local disk
     so multi-replica pods share them.
  2. /api/upload/extract is ALWAYS async when PDF chunks are involved.
  3. /api/extract-document-text is ALWAYS async when a PDF is in the payload,
     but may remain sync for small non-PDF payloads.
  4. Error case: /api/upload/extract with unknown upload_id → 404.
"""
import os
import io
import time
import base64
import uuid
import pytest
import requests

def _load_backend_url():
    v = os.environ.get("REACT_APP_BACKEND_URL")
    if v:
        return v.rstrip("/")
    # Fallback: read from /app/frontend/.env
    try:
        with open("/app/frontend/.env") as f:
            for line in f:
                line = line.strip()
                if line.startswith("REACT_APP_BACKEND_URL="):
                    return line.split("=", 1)[1].strip().rstrip("/")
    except Exception:
        pass
    raise RuntimeError("REACT_APP_BACKEND_URL not set")


def _load_mongo():
    url = os.environ.get("MONGO_URL")
    dbn = os.environ.get("DB_NAME")
    if url and dbn:
        return url, dbn
    try:
        with open("/app/backend/.env") as f:
            for line in f:
                line = line.strip()
                if line.startswith("MONGO_URL="):
                    url = line.split("=", 1)[1].strip()
                elif line.startswith("DB_NAME="):
                    dbn = line.split("=", 1)[1].strip()
    except Exception:
        pass
    return url, dbn


BASE_URL = _load_backend_url()
API = f"{BASE_URL}/api"

CHUNK0 = "/tmp/ocr/chunk_0000"
CHUNK1 = "/tmp/ocr/chunk_0001"
FULL_PDF = "/tmp/ocr/rapport.pdf"


# -------- helpers --------
def _poll_status(extraction_id: str, max_seconds: int = 240, interval: int = 8):
    """Poll /api/upload/extract-status/{id} until done or timeout."""
    deadline = time.time() + max_seconds
    last = None
    while time.time() < deadline:
        r = requests.get(f"{API}/upload/extract-status/{extraction_id}", timeout=90)
        if r.status_code != 200:
            last = {"http": r.status_code, "text": r.text[:200]}
            time.sleep(interval)
            continue
        data = r.json()
        last = data
        status = data.get("status")
        if status in ("done", "error"):
            return data
        time.sleep(interval)
    return {"status": "timeout", "last": last}


# -------- 1. Chunked upload multi-replica (MongoDB chunks) --------

class TestChunkedUploadMongo:
    """BUG FIX 1: chunks stored in MongoDB, /extract always async."""

    def test_full_chunked_flow_scan_pdf(self):
        """Upload chunk_0000 + chunk_0001, extract async, poll until done."""
        assert os.path.exists(CHUNK0), "chunk_0000 missing"
        assert os.path.exists(CHUNK1), "chunk_0001 missing"

        upload_id = f"TEST_{uuid.uuid4().hex[:12]}"
        filename = "rapport.pdf"

        # --- chunk 0 ---
        with open(CHUNK0, "rb") as f:
            r0 = requests.post(
                f"{API}/upload/chunk",
                data={"upload_id": upload_id, "filename": filename,
                      "chunk_index": 0, "total_chunks": 2},
                files={"chunk": ("chunk_0000", f, "application/octet-stream")},
                timeout=60,
            )
        assert r0.status_code == 200, f"chunk0 http={r0.status_code} body={r0.text[:200]}"
        j0 = r0.json()
        assert j0["received"] == 1
        assert j0["complete"] is False

        # --- chunk 1 ---
        with open(CHUNK1, "rb") as f:
            r1 = requests.post(
                f"{API}/upload/chunk",
                data={"upload_id": upload_id, "filename": filename,
                      "chunk_index": 1, "total_chunks": 2},
                files={"chunk": ("chunk_0001", f, "application/octet-stream")},
                timeout=60,
            )
        assert r1.status_code == 200
        j1 = r1.json()
        assert j1["received"] == 2
        assert j1["complete"] is True

        # --- extract (should be async immediately) ---
        t0 = time.time()
        r = requests.post(
            f"{API}/upload/extract",
            json={
                "upload_id": upload_id,
                "files": [{
                    "name": filename,
                    "type": "application/pdf",
                    "total_chunks": 2,
                    "chunked": True,
                }],
            },
            timeout=30,
        )
        elapsed = time.time() - t0
        assert r.status_code == 200, f"extract http={r.status_code} body={r.text[:300]}"
        j = r.json()
        assert j.get("async") is True, f"expected async=true, got {j}"
        assert "extraction_id" in j
        extraction_id = j["extraction_id"]
        assert elapsed < 15, f"async response should be fast, took {elapsed:.1f}s"

        # --- verify chunks were cleaned up from Mongo (after reassembly, before polling) ---
        from pymongo import MongoClient
        mongo_url, db_name = _load_mongo()
        client = MongoClient(mongo_url)
        try:
            remaining = client[db_name].upload_chunks.count_documents({"upload_id": upload_id})
        finally:
            client.close()
        assert remaining == 0, f"Chunks not cleaned up after reassembly: {remaining} left"

        # --- poll for completion ---
        final = _poll_status(extraction_id, max_seconds=240, interval=8)
        assert final.get("status") == "done", f"extraction did not complete: {final}"
        extracted = final.get("extracted_text", "")
        details = final.get("details", [])
        assert len(extracted) > 5000, f"extracted_text too short ({len(extracted)} chars)"
        assert details, "details missing"
        d0 = details[0]
        assert d0.get("has_text") is True
        # Method should mention Gemini Vision for scanned PDF
        method = str(d0.get("method", ""))
        assert "gemini" in method.lower() or "vision" in method.lower(), f"unexpected method: {method}"


# -------- 2. MongoDB indexes exist --------

class TestUploadChunksIndexes:
    """Verify TTL + unique compound index on upload_chunks."""

    def test_indexes_present(self):
        # Trigger index init by sending a tiny chunk
        upload_id = f"TEST_IDX_{uuid.uuid4().hex[:8]}"
        r = requests.post(
            f"{API}/upload/chunk",
            data={"upload_id": upload_id, "filename": "tiny.bin",
                  "chunk_index": 0, "total_chunks": 1},
            files={"chunk": ("tiny.bin", io.BytesIO(b"x" * 32), "application/octet-stream")},
            timeout=15,
        )
        assert r.status_code == 200

        # Inspect indexes directly via Mongo
        from pymongo import MongoClient
        mongo_url, db_name = _load_mongo()
        assert mongo_url and db_name, "MONGO_URL/DB_NAME missing"
        client = MongoClient(mongo_url)
        try:
            db = client[db_name]
            info = db.upload_chunks.index_information()
            # TTL index on created_at_dt
            ttl_ok = any(
                idx.get("expireAfterSeconds") == 3600
                and any(k == "created_at_dt" for k, _ in idx.get("key", []))
                for idx in info.values()
            )
            assert ttl_ok, f"TTL index missing: {info}"
            # Unique compound index
            uniq_ok = any(
                idx.get("unique") and
                [k for k, _ in idx.get("key", [])] == ["upload_id", "safe_name", "chunk_index"]
                for idx in info.values()
            )
            assert uniq_ok, f"unique compound index missing: {info}"

            # Cleanup our test chunk
            db.upload_chunks.delete_many({"upload_id": upload_id})
        finally:
            client.close()


# -------- 3. /extract-document-text base64 with PDF → async --------

class TestExtractDocumentTextAsync:
    """BUG FIX 2: base64 extraction is always async when a PDF is present."""

    def test_small_pdf_base64_returns_async(self):
        # Minimal fake PDF bytes — routing check only looks at file type/name,
        # not content, when deciding sync vs async. This keeps payload tiny.
        pdf_bytes = b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF\n"
        b64 = base64.b64encode(pdf_bytes).decode()
        t0 = time.time()
        r = requests.post(
            f"{API}/extract-document-text",
            json={"files": [{"name": "tiny.pdf", "type": "application/pdf", "data": b64}]},
            timeout=30,
        )
        elapsed = time.time() - t0
        assert r.status_code == 200, f"http={r.status_code} body={r.text[:200]}"
        j = r.json()
        assert j.get("async") is True, f"PDF payload must be async, got: {j}"
        assert "extraction_id" in j
        assert elapsed < 15, f"async response too slow: {elapsed:.1f}s"

        # Poll briefly just to confirm the job exists
        eid = j["extraction_id"]
        r2 = requests.get(f"{API}/upload/extract-status/{eid}", timeout=20)
        assert r2.status_code == 200
        assert r2.json().get("status") in ("queued", "processing", "done", "error")

    def test_small_text_stays_sync(self):
        # small .txt payload should NOT be async
        content = b"Hello world - small text file, well under 1MB, no PDF." * 5
        b64 = base64.b64encode(content).decode()
        r = requests.post(
            f"{API}/extract-document-text",
            json={"files": [{"name": "note.txt", "type": "text/plain", "data": b64}]},
            timeout=60,
        )
        assert r.status_code == 200, f"http={r.status_code} body={r.text[:200]}"
        j = r.json()
        # Not async — should have extracted_text directly
        assert j.get("async") is not True, f"text file should stay sync, got: {j}"
        assert "extracted_text" in j or "files_processed" in j


# -------- 4. Error case: unknown upload_id --------

class TestExtractErrorCases:
    def test_unknown_upload_id_returns_404(self):
        r = requests.post(
            f"{API}/upload/extract",
            json={
                "upload_id": f"TEST_MISSING_{uuid.uuid4().hex[:8]}",
                "files": [{
                    "name": "ghost.pdf", "type": "application/pdf",
                    "total_chunks": 2, "chunked": True,
                }],
            },
            timeout=10,
        )
        assert r.status_code == 404, f"expected 404, got {r.status_code}: {r.text[:200]}"
        assert "non trouve" in r.text.lower() or "not found" in r.text.lower()


# -------- 5. Smoke health --------

class TestHealthSmoke:
    def test_health_pdf_fonts_ok(self):
        r = requests.get(f"{API}/health", timeout=30)
        assert r.status_code == 200
        j = r.json()
        assert j.get("status") == "healthy"
        pdf_fonts = j.get("pdf_fonts") or {}
        assert pdf_fonts.get("ok") is True, f"pdf_fonts not ok: {pdf_fonts}"
