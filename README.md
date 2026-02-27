# ai_company CrewAI V1

This repository contains a complete, runnable V1 CrewAI scaffold for a multi-team AI organization:

- Global orchestrator flow (human CEO input)
- Technical crew
- Compliance/legal crew
- Marketing/communication crew
- Finance crew

The CEO is explicitly human-in-the-loop and is not implemented as an agent.

## Project Structure

Core implementation is under `src/company_ai/`:

- `main.py`: global orchestration flow
- `tools/`: safe local tools and stubs
- `crews/`: domain crews with YAML-based agent/task definitions
- `artifacts/`: generated output files

## Assumptions

- CrewAI API surface can vary across versions; this project uses a simple `Flow` + sequential `Crew` pattern compatible with current V1-style usage.
- LLM provider credentials and model selection are provided via environment variables.
- All write operations are local and file-based; no deployment or remote execution is included.
- Stub tools (`ContractReviewTool`, `ComplianceChecklistTool`, `ClaimsCheckTool`, `CostModelTool`) intentionally provide deterministic placeholders and are not production-grade analyzers.

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -e .
```

3. Create your environment file:

```bash
copy .env.example .env
```

4. Populate `.env` with your own values.

## Run

Provide a CEO request as a single command-line argument:

```bash
python -m company_ai.main "Launch an AI-powered compliance assistant for SMB clients in 90 days."
```

Generated outputs are written under `src/company_ai/artifacts/`.

## Notes on Safety

- No real secrets are committed.
- `WriteArtifactTool` only writes under `src/company_ai/artifacts/`.
- `RepoWriteTool` is intentionally simple and includes comments warning about repository write risk.
- `RunTestsTool` and `RunLintTool` execute local shell commands only.
