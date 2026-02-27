from __future__ import annotations

import json
import subprocess
from pathlib import Path

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


class CommandInput(BaseModel):
    command: str = Field(description="Shell command to execute")


class RunTestsTool(BaseTool):
    name: str = "run_tests"
    description: str = "Run a local test command and return stdout/stderr/exit code."
    args_schema: type[BaseModel] = CommandInput

    def _run(self, command: str) -> str:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=_repo_root(),
            timeout=180,
        )
        return json.dumps(
            {
                "command": command,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            },
            indent=2,
        )


class RunLintTool(BaseTool):
    name: str = "run_lint"
    description: str = "Run a local lint command and return stdout/stderr/exit code."
    args_schema: type[BaseModel] = CommandInput

    def _run(self, command: str) -> str:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=_repo_root(),
            timeout=180,
        )
        return json.dumps(
            {
                "command": command,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            },
            indent=2,
        )
