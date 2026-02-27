from __future__ import annotations

import json
import re

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class ClaimsCheckInput(BaseModel):
    text: str = Field(description="Marketing copy to check")


class ClaimsCheckTool(BaseTool):
    name: str = "claims_check"
    description: str = "Flag risky marketing wording using simple heuristics."
    args_schema: type[BaseModel] = ClaimsCheckInput

    def _run(self, text: str) -> str:
        risky_patterns = [
            r"\bguarantee(d)?\b",
            r"\bzero risk\b",
            r"\b100%\b",
            r"\balways\b",
            r"\bnever fails?\b",
        ]
        flags = [pattern for pattern in risky_patterns if re.search(pattern, text, re.IGNORECASE)]
        return json.dumps(
            {
                "risk_count": len(flags),
                "matched_patterns": flags,
                "recommendation": (
                    "Replace absolute claims with measurable and qualified language."
                    if flags
                    else "No obvious risky claims detected."
                ),
            },
            indent=2,
        )
