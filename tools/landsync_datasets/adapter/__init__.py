"""
LANDSYNC AI integration adapter package.
"""

from landsync_datasets.adapter.landsync_adapter import (
    to_landsync_parcel,
    to_landsync_document,
    HAS_LANDSYNC_APP,
)

__all__ = ["to_landsync_parcel", "to_landsync_document", "HAS_LANDSYNC_APP"]
