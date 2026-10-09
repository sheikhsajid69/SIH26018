"""
Legal research register and rule catalogue for LANDSYNC benchmark.
"""

from landsync_datasets.legal.rule_register import (
    LEGAL_RULES,
    get_rule_by_id,
    get_all_rules,
)

__all__ = ["LEGAL_RULES", "get_rule_by_id", "get_all_rules"]
