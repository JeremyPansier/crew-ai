from __future__ import annotations

import json

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class ContractReviewInput(BaseModel):
    document_summary: str = Field(description="Short summary of the contract or policy")


class ComplianceChecklistInput(BaseModel):
    product_scope: str = Field(description="Product or initiative scope")


class ContractReviewTool(BaseTool):
    name: str = "contract_review"
    description: str = "Return a simple legal review placeholder structure."
    args_schema = ContractReviewInput

    def _run(self, document_summary: str) -> str:
        return json.dumps(
            {
                "document_summary": document_summary,
                "risk_level": "medium",
                "key_concerns": [
                    "Data processing terms need explicit consent language.",
                    "Liability limitations should be reviewed against jurisdiction.",
                    "Retention policy references need to match internal policy.",
                ],
                "recommended_actions": [
                    "Request legal redline review.",
                    "Confirm regulatory references are up to date.",
                ],
            },
            indent=2,
        )


class ComplianceChecklistTool(BaseTool):
    name: str = "compliance_checklist"
    description: str = "Return a baseline compliance checklist template."
    args_schema = ComplianceChecklistInput

    def _run(self, product_scope: str) -> str:
        return json.dumps(
            {
                "scope": product_scope,
                "checklist": [
                    {"item": "Data classification completed", "status": "pending"},
                    {"item": "Privacy notice updated", "status": "pending"},
                    {"item": "Access controls documented", "status": "pending"},
                    {"item": "Audit logging requirements defined", "status": "pending"},
                    {"item": "Incident response ownership assigned", "status": "pending"},
                ],
            },
            indent=2,
        )
