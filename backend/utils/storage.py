import os
import uuid
import logging

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

# Configuration : S3 compatible (AWS, MinIO, Scaleway, OVH, etc.)
S3_ENDPOINT = os.environ.get("S3_ENDPOINT", "")
S3_ACCESS_KEY = os.environ.get("S3_ACCESS_KEY", "")
S3_SECRET_KEY = os.environ.get("S3_SECRET_KEY", "")
S3_BUCKET = os.environ.get("S3_BUCKET", "strategie-expertise-sante")
S3_REGION = os.environ.get("S3_REGION", "eu-west-3")

APP_NAME = "strategie-expertise-sante"

_s3_client = None


def _get_s3():
    global _s3_client
    if _s3_client:
        return _s3_client
    if not S3_ACCESS_KEY or not S3_SECRET_KEY:
        raise RuntimeError("S3 non configuré : S3_ACCESS_KEY / S3_SECRET_KEY manquants")
    kwargs = {
        "service_name": "s3",
        "aws_access_key_id": S3_ACCESS_KEY,
        "aws_secret_access_key": S3_SECRET_KEY,
        "region_name": S3_REGION,
    }
    if S3_ENDPOINT:
        kwargs["endpoint_url"] = S3_ENDPOINT
    _s3_client = boto3.client(**kwargs)
    logger.info("Object storage (S3) initialized")
    return _s3_client


MIME_TYPES = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "gif": "image/gif",
    "webp": "image/webp",
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "txt": "text/plain",
    "csv": "text/csv",
}


def put_object(path: str, data: bytes, content_type: str) -> dict:
    s3 = _get_s3()
    s3.put_object(Bucket=S3_BUCKET, Key=path, Body=data, ContentType=content_type)
    return {"path": path, "size": len(data)}


def get_object(path: str) -> tuple:
    s3 = _get_s3()
    resp = s3.get_object(Bucket=S3_BUCKET, Key=path)
    content = resp["Body"].read()
    content_type = resp.get("ContentType", "application/octet-stream")
    return content, content_type


def upload_file(user_id: str, filename: str, data: bytes, content_type: str) -> dict:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "bin"
    if not content_type or content_type == "application/octet-stream":
        content_type = MIME_TYPES.get(ext, "application/octet-stream")
    storage_path = f"{APP_NAME}/uploads/{user_id}/{uuid.uuid4()}.{ext}"
    result = put_object(storage_path, data, content_type)
    return {
        "storage_path": result["path"],
        "original_filename": filename,
        "content_type": content_type,
        "size": result.get("size", len(data)),
    }


def download_file(storage_path: str) -> tuple:
    return get_object(storage_path)


def delete_object(path: str) -> bool:
    try:
        s3 = _get_s3()
        s3.delete_object(Bucket=S3_BUCKET, Key=path)
        return True
    except ClientError as e:
        logger.warning(f"Failed to delete S3 object {path}: {e}")
        return False


def generate_presigned_url(path: str, expires_in: int = 3600) -> str:
    """Generate a presigned URL for secure, temporary access to a document."""
    try:
        s3 = _get_s3()
        url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": S3_BUCKET, "Key": path},
            ExpiresIn=expires_in,
        )
        return url
    except Exception as e:
        logger.warning(f"Failed to generate presigned URL for {path}: {e}")
        return ""


def ensure_bucket():
    """Create bucket if it doesn't exist, block public access."""
    try:
        s3 = _get_s3()
        try:
            s3.head_bucket(Bucket=S3_BUCKET)
            logger.info(f"S3 bucket '{S3_BUCKET}' exists")
        except ClientError:
            s3.create_bucket(
                Bucket=S3_BUCKET,
                CreateBucketConfiguration={"LocationConstraint": S3_REGION},
            )
            logger.info(f"S3 bucket '{S3_BUCKET}' created")

        s3.put_public_access_block(
            Bucket=S3_BUCKET,
            PublicAccessBlockConfiguration={
                "BlockPublicAcls": True,
                "IgnorePublicAcls": True,
                "BlockPublicPolicy": True,
                "RestrictPublicBuckets": True,
            },
        )
    except Exception as e:
        logger.warning(f"Bucket init warning: {e}")
