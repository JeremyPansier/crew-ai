from __future__ import annotations

from pathlib import Path

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class WriteArtifactInput(BaseModel):
    relative_path: str = Field(description="Path under src/company_ai/artifacts/")
    content: str = Field(description="Text content to write")


class WriteArtifactTool(BaseTool):
    name: str = "write_artifact"
    description: str = "Write a text artifact safely under src/company_ai/artifacts/."
    args_schema: type[BaseModel] = WriteArtifactInput

    def _artifacts_root(self) -> Path:
        return Path(__file__).resolve().parents[1] / "artifacts"

    def _safe_path(self, relative_path: str) -> Path:
        root = self._artifacts_root().resolve()
        target = (root / relative_path).resolve()
        if not str(target).startswith(str(root)):
            raise ValueError("Path traversal detected. Write denied.")
        return target

    def _run(self, relative_path: str, content: str) -> str:
        target = self._safe_path(relative_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"Artifact written: {target}"
