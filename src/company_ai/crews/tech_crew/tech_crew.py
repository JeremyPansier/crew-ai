from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from crewai import Agent, Crew, Process, Task

from company_ai.tools import RepoReadTool, RunLintTool, RunTestsTool, WriteArtifactTool


class TechnicalCrew:
    def __init__(self) -> None:
        self.base_dir = Path(__file__).resolve().parent
        self.agents_config = self._load_yaml(self.base_dir / "config" / "agents.yaml")
        self.tasks_config = self._load_yaml(self.base_dir / "config" / "tasks.yaml")

    @staticmethod
    def _load_yaml(path: Path) -> dict[str, Any]:
        return yaml.safe_load(path.read_text(encoding="utf-8"))

    def _build_agents(self) -> dict[str, Agent]:
        write_tool = WriteArtifactTool()
        repo_read = RepoReadTool()
        run_tests = RunTestsTool()
        run_lint = RunLintTool()

        def mk(name: str, tools: list[Any] | None = None) -> Agent:
            cfg = self.agents_config[name]
            return Agent(
                role=cfg["role"],
                goal=cfg["goal"],
                backstory=cfg["backstory"],
                allow_delegation=cfg.get("allow_delegation", False),
                verbose=cfg.get("verbose", False),
                tools=tools or [],
            )

        return {
            "cto": mk("cto", [repo_read]),
            "product_owner": mk("product_owner", [write_tool]),
            "software_architect": mk("software_architect", [write_tool]),
            "tech_lead": mk("tech_lead", [write_tool]),
            "backend_developer": mk("backend_developer", [write_tool, repo_read]),
            "frontend_developer": mk("frontend_developer", [write_tool, repo_read]),
            "devops_engineer": mk("devops_engineer", [write_tool]),
            "qa_tester": mk("qa_tester", [write_tool, run_tests, run_lint]),
            "ui_designer": mk("ui_designer", [write_tool]),
            "ux_designer": mk("ux_designer", [write_tool]),
        }

    def _build_tasks(self, agents: dict[str, Agent], ceo_request: str) -> list[Task]:
        ordered_task_keys = [
            "product_scoping",
            "ux_flows",
            "ui_specs",
            "architecture",
            "implementation_plan",
            "backend_implementation",
            "frontend_implementation",
            "devops_pipeline_setup",
            "qa_validation",
            "final_technical_review",
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
