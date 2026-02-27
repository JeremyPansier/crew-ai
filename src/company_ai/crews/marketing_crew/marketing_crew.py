from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from crewai import Agent, Crew, Process, Task

from company_ai.tools import ClaimsCheckTool, WriteArtifactTool, build_internet_tools


class MarketingCrew:
    def __init__(self) -> None:
        self.base_dir = Path(__file__).resolve().parent
        self.agents_config = self._load_yaml(self.base_dir / "config" / "agents.yaml")
        self.tasks_config = self._load_yaml(self.base_dir / "config" / "tasks.yaml")

    @staticmethod
    def _load_yaml(path: Path) -> dict[str, Any]:
        return yaml.safe_load(path.read_text(encoding="utf-8"))

    def _build_agents(self) -> dict[str, Agent]:
        write_tool = WriteArtifactTool()
        claims_check = ClaimsCheckTool()

        def mk(name: str, tools: list[Any] | None = None) -> Agent:
            cfg = self.agents_config[name]
            role_tools = [*build_internet_tools(), *(tools or [])]
            return Agent(
                role=cfg["role"],
                goal=cfg["goal"],
                backstory=cfg["backstory"],
                allow_delegation=cfg.get("allow_delegation", False),
                verbose=cfg.get("verbose", False),
                tools=role_tools,
            )

        return {
            "cmo": mk("cmo", [write_tool]),
            "marketing_strategist": mk("marketing_strategist", [write_tool]),
            "copywriter_communications": mk("copywriter_communications", [write_tool]),
            "brand_communications_reviewer": mk("brand_communications_reviewer", [claims_check]),
        }

    def _build_tasks(self, agents: dict[str, Agent], ceo_request: str) -> list[Task]:
        ordered_task_keys = [
            "strategy_brief",
            "announcement_drafting",
            "brand_review",
            "cmo_approval_gate",
        ]
        tasks: list[Task] = []
        for task_key in ordered_task_keys:
            cfg = self.tasks_config[task_key]
            tasks.append(
                Task(
                    description=cfg["description"].format(ceo_request=ceo_request),
                    expected_output=cfg["expected_output"],
                    agent=agents[cfg["agent"]],
                    output_file=cfg["output_file"],
                )
            )
        return tasks

    def crew(self, ceo_request: str) -> Crew:
        agents = self._build_agents()
        tasks = self._build_tasks(agents, ceo_request)
        return Crew(
            agents=list(agents.values()),
            tasks=tasks,
            process=Process.sequential,
            verbose=True,
        )

    def run(self, ceo_request: str) -> str:
        result = self.crew(ceo_request).kickoff(inputs={"ceo_request": ceo_request})
        return str(result)
