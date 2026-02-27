from __future__ import annotations

import json

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class CostModelInput(BaseModel):
    initiative: str = Field(description="Name or summary of the initiative")


class CostModelTool(BaseTool):
    name: str = "cost_model"
    description: str = "Return a low/base/high cost estimation template."
    args_schema = CostModelInput

    def _run(self, initiative: str) -> str:
        return json.dumps(
            {
                "initiative": initiative,
                "currency": "USD",
                "estimate": {
                    "low": 50000,
                    "base": 90000,
                    "high": 150000,
                },
                "drivers": [
                    "Engineering staffing",
                    "Model/API usage",
                    "Security and compliance review effort",
                    "QA and release hardening",
                ],
            },
            indent=2,
        )
