from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path


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
        return f"/api/v1/documents/raw?key={storage_key}"

    def exists(self, storage_key: str) -> bool:
        target = (self.root / storage_key).resolve()
        try:
            return str(target).startswith(str(self.root)) and target.is_file()
        except Exception:
            return False


# Alias for type compatibility
EvidenceStorageProvider = LocalEvidenceStorage


def get_storage_provider() -> LocalEvidenceStorage:
    """Return local evidence storage instance."""
    root = os.getenv("LOCAL_STORAGE_ROOT", ".landsync-storage")
    return LocalEvidenceStorage(root=root)

