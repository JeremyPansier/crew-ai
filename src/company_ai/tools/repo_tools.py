from __future__ import annotations

from pathlib import Path

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


class RepoReadInput(BaseModel):
    file_path: str = Field(description="Repository-relative text file path")


class RepoWriteInput(BaseModel):
    file_path: str = Field(description="Repository-relative text file path")
    content: str = Field(description="Content to write")


class RepoReadTool(BaseTool):
    name: str = "repo_read"
    description: str = "Read a text file from the repository."
    args_schema: type[BaseModel] = RepoReadInput

    def _run(self, file_path: str) -> str:
        target = (_repo_root() / file_path).resolve()
        if not target.exists() or not target.is_file():
            return f"File not found: {file_path}"
        return target.read_text(encoding="utf-8")


class RepoWriteTool(BaseTool):
    name: str = "repo_write"
    description: str = "Write a text file in the repository."
    args_schema: type[BaseModel] = RepoWriteInput

    def _run(self, file_path: str, content: str) -> str:
        # This tool intentionally allows repository writes for scaffolding workflows.
        # Use with care because it can overwrite existing files.
        target = (_repo_root() / file_path).resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"Wrote file: {target}"
