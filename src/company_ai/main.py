from __future__ import annotations

import sys
from pathlib import Path

from pydantic import BaseModel, Field

from crewai.flow.flow import Flow, listen, start

from company_ai.crews.compliance_crew import ComplianceCrew
from company_ai.crews.finance_crew import FinanceCrew
from company_ai.crews.marketing_crew import MarketingCrew
from company_ai.crews.tech_crew import TechnicalCrew


class OrganizationState(BaseModel):
    ceo_request: str = Field(default="")
    technical_output: str = Field(default="")
    finance_output: str = Field(default="")
    compliance_output: str = Field(default="")
    marketing_output: str = Field(default="")
    final_report_path: str = Field(default="src/company_ai/artifacts/reports/final_orchestration_report.md")


class OrganizationFlow(Flow[OrganizationState]):
    initial_state = OrganizationState

    @start()
    def run_technical(self) -> str:
        ceo_request = self.state.ceo_request.strip()
        if not ceo_request:
            raise ValueError("CEO request is required.")
        self.state.technical_output = TechnicalCrew().run(ceo_request)
        return self.state.technical_output

    @listen(run_technical)
    def run_finance_and_compliance(self) -> dict[str, str]:
        ceo_request = self.state.ceo_request
        self.state.finance_output = FinanceCrew().run(ceo_request)
        self.state.compliance_output = ComplianceCrew().run(ceo_request)
        return {
            "finance_output": self.state.finance_output,
            "compliance_output": self.state.compliance_output,
        }

    @listen(run_finance_and_compliance)
    def run_marketing(self) -> str:
        ceo_request = self.state.ceo_request
        self.state.marketing_output = MarketingCrew().run(ceo_request)
        return self.state.marketing_output

    @listen(run_marketing)
    def finalize(self) -> str:
        report_path = Path(self.state.final_report_path)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            "\n".join(
                [
                    "# ai_company Orchestration Report",
                    "",
                    f"## CEO Request",
                    self.state.ceo_request,
                    "",
                    "## Technical Crew Output",
                    self.state.technical_output,
                    "",
                    "## Finance Crew Output",
                    self.state.finance_output,
                    "",
                    "## Compliance Crew Output",
                    self.state.compliance_output,
                    "",
                    "## Marketing Crew Output",
                    self.state.marketing_output,
                ]
            ),
            encoding="utf-8",
        )
        return str(report_path)


def run_flow(ceo_request: str) -> str:
    flow = OrganizationFlow()
    result = flow.kickoff(inputs={"ceo_request": ceo_request})
    return str(result)


def main() -> int:
    if len(sys.argv) < 2:
        print('Usage: python -m company_ai.main "CEO request here"')
        return 1
    ceo_request = " ".join(sys.argv[1:]).strip()
    result = run_flow(ceo_request)
    print(f"Flow completed. Final report: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
