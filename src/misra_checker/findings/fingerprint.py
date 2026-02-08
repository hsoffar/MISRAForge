from __future__ import annotations

import hashlib

from misra_checker.core.models import Finding


def finding_fingerprint(finding: Finding) -> str:
    payload = "|".join(
        [
            finding.rule_id,
            finding.location.path,
            str(finding.location.line),
            str(finding.location.column),
            finding.message,
        ]
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
