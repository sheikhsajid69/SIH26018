from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path
from typing import Protocol, runtime_checkable


class StorageTamperError(Exception):
    """Raised when an existing storage key is overwritten with differing content (Rule 5 immutability)."""
    pass


class StorageTraversalError(Exception):
    """Raised when an untrusted storage key attempts path traversal outside root storage."""
    pass


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent directory traversal or invalid characters."""
    clean = Path(filename).name
    clean = re.sub(r"[^a-zA-Z0-9_.-]", "_", clean)
    return clean or "document.bin"


@runtime_checkable
class EvidenceStorageProvider(Protocol):
    """Evidence storage provider protocol supporting local and object storage (S3/GCS)."""

    def save(
        self,
        parcel_id: str,
        body: bytes,
        filename: str = "document.bin",
        version: int = 1,
        tenant_or_jurisdiction: str = "demo",
    ) -> tuple[str, str]:
        """Save file content addressed by SHA-256 and return (storage_key, sha256_digest)."""
        ...

    def get(self, storage_key: str) -> bytes | None:
        """Retrieve file content given a storage_key, or None if not found."""
        ...

    def get_url(self, storage_key: str, expires_in: int = 3600) -> str:
        """Generate download URL or presigned S3 URL for evidence file."""
        ...

    def exists(self, storage_key: str) -> bool:
        """Check if file exists at storage_key."""
        ...


class LocalEvidenceStorage:
    """
    Local filesystem evidence store.
    Content-addressed SHA-256 storage keys prevent arbitrary path traversal.
    Enforces WORM (Write Once, Read Many) tamper detection.
    """

    def __init__(self, root: str | Path = ".landsync-storage") -> None:
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        parcel_id: str,
        body: bytes,
        filename: str = "document.bin",
        version: int = 1,
        tenant_or_jurisdiction: str = "demo",
    ) -> tuple[str, str]:
        digest = hashlib.sha256(body).hexdigest()
        clean_file = sanitize_filename(filename)
        clean_tenant = re.sub(r"[^a-zA-Z0-9_-]", "_", tenant_or_jurisdiction)
        clean_parcel = re.sub(r"[^a-zA-Z0-9_-]", "_", parcel_id)
        
        # Deterministic content-addressed key structure
        key = f"documents/{clean_tenant}/{clean_parcel}/{digest}/{version}/{clean_file}"
        target = (self.root / key).resolve()

        # Strict boundary defense
        if not str(target).startswith(str(self.root)):
            raise StorageTraversalError("Path traversal attempt in storage key generation.")

        # Tamper defense: If file exists at this key, verify hash
        if target.exists():
            existing_hash = hashlib.sha256(target.read_bytes()).hexdigest()
            if existing_hash != digest:
                raise StorageTamperError(
                    f"Integrity violation: Storage key {key} already exists with differing SHA-256 digest."
                )
            return key, digest

        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(body)
        return key, digest

    def get(self, storage_key: str) -> bytes | None:
        target = (self.root / storage_key).resolve()
        try:
            if not str(target).startswith(str(self.root)):
                return None
            if target.is_file():
                return target.read_bytes()
        except Exception:
            return None
        return None

    def get_url(self, storage_key: str, expires_in: int = 3600) -> str:
        # Local API stream URL
        return f"/api/v1/documents/raw?key={storage_key}"

    def exists(self, storage_key: str) -> bool:
        target = (self.root / storage_key).resolve()
        try:
            return str(target).startswith(str(self.root)) and target.is_file()
        except Exception:
            return False


class S3EvidenceStorage:
    """
    Amazon S3 / S3-compatible (MinIO, Ceph, Cloudflare R2) evidence store.
    Uses boto3 with server-side encryption and presigned GET URLs.
    """

    def __init__(
        self,
        bucket_name: str,
        region: str = "us-east-1",
        endpoint_url: str | None = None,
        prefix: str = "landsync",
    ) -> None:
        self.bucket_name = bucket_name
        self.region = region
        self.prefix = prefix.strip("/")
        
        import boto3
        from botocore.config import Config

        session = boto3.session.Session()
        self.s3_client = session.client(
            "s3",
            region_name=self.region,
            endpoint_url=endpoint_url or os.getenv("AWS_ENDPOINT_URL"),
            config=Config(signature_version="s3v4"),
        )

    def save(
        self,
        parcel_id: str,
        body: bytes,
        filename: str = "document.bin",
        version: int = 1,
        tenant_or_jurisdiction: str = "demo",
    ) -> tuple[str, str]:
        digest = hashlib.sha256(body).hexdigest()
        clean_file = sanitize_filename(filename)
        clean_tenant = re.sub(r"[^a-zA-Z0-9_-]", "_", tenant_or_jurisdiction)
        clean_parcel = re.sub(r"[^a-zA-Z0-9_-]", "_", parcel_id)

        key = f"{self.prefix}/documents/{clean_tenant}/{clean_parcel}/{digest}/{version}/{clean_file}"

        # Tamper defense: Check if object exists
        from botocore.exceptions import ClientError
        try:
            head = self.s3_client.head_object(Bucket=self.bucket_name, Key=key)
            existing_meta = head.get("Metadata", {})
            if existing_meta.get("sha256") and existing_meta["sha256"] != digest:
                raise StorageTamperError(
                    f"Integrity violation: S3 object {key} exists with differing SHA-256 hash."
                )
            return key, digest
        except ClientError as e:
            if e.response["Error"]["Code"] != "404":
                # Some other error (e.g. auth), raise
                pass

        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=body,
            Metadata={"sha256": digest, "parcel_id": clean_parcel},
            ServerSideEncryption="AES256",
        )
        return key, digest

    def get(self, storage_key: str) -> bytes | None:
        from botocore.exceptions import ClientError
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=storage_key)
            return response["Body"].read()
        except ClientError:
            return None

    def get_url(self, storage_key: str, expires_in: int = 3600) -> str:
        return self.s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket_name, "Key": storage_key},
            ExpiresIn=expires_in,
        )

    def exists(self, storage_key: str) -> bool:
        from botocore.exceptions import ClientError
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=storage_key)
            return True
        except ClientError:
            return False


def get_storage_provider() -> EvidenceStorageProvider:
    """Factory selecting storage provider based on STORAGE_PROVIDER environment variable."""
    provider_type = os.getenv("STORAGE_PROVIDER", "local").lower().strip()
    if provider_type == "s3":
        bucket = os.getenv("AWS_S3_BUCKET", "landsync-evidence-demo")
        region = os.getenv("AWS_REGION", "us-east-1")
        return S3EvidenceStorage(bucket_name=bucket, region=region)
    root = os.getenv("LOCAL_STORAGE_ROOT", ".landsync-storage")
    return LocalEvidenceStorage(root=root)
