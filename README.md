# ai_company CrewAI V1

This repository contains a complete, runnable V1 CrewAI scaffold for a multi-team AI organization:

- Global orchestrator flow (human CEO input)
- Technical crew
- Compliance/legal crew
- Marketing/communication crew
- Finance crew

The CEO is explicitly human-in-the-loop and is not implemented as an agent.

All agents now have internet research capability in addition to their existing local role-specific tools.

## Project Structure

Core implementation is under `src/company_ai/`:

- `main.py`: global orchestration flow
- `tools/`: safe local tools and stubs
- `crews/`: domain crews with YAML-based agent/task definitions
- `artifacts/`: generated output files

## Assumptions

- CrewAI API surface can vary across versions; this project uses a simple `Flow` + sequential `Crew` pattern compatible with current V1-style usage.
- Internet search uses `InternetSearchTool` with provider selection:
  - Serper (when `SERPER_API_KEY` is set)
  - DuckDuckGo HTML fallback (when `SERPER_API_KEY` is not set)
- Web reading uses `ReadWebpageTool` for direct HTTP/HTTPS page retrieval.
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

Environment variables:

- `OPENAI_API_KEY`: required for CrewAI LLM calls.
- `OPENAI_MODEL_NAME`: model name to use.
- `SERPER_API_KEY`: optional but recommended for higher quality web search results.
- `INTERNET_TOOL_TIMEOUT_SECONDS`: optional HTTP timeout for web tools.
- `INTERNET_TOOL_USER_AGENT`: optional user-agent header used by web tools.

## Run

Provide a CEO request as a single command-line argument:

```bash
python -m company_ai.main "Launch an AI-powered compliance assistant for SMB clients in 90 days."
```

Generated outputs are written under `src/company_ai/artifacts/`.

## Internet Tools Added

Every agent in all crews receives:

- `internet_search`: web search for current/public information.
- `read_webpage`: direct webpage retrieval and text extraction.

Each agent keeps its original local tools (artifact writing, repo read, lint/test runner, legal/marketing/finance stubs).

## What Is Stubbed vs Production-Ready

- Stubbed (deterministic placeholders): legal review/checklist, marketing claims check, finance cost model.
- Practical but lightweight internet tooling: search and webpage reading.
- Not included: deployment automation, background schedulers, secret managers, privileged runtime execution.

## Notes on Safety

- No real secrets are committed.
- `WriteArtifactTool` only writes under `src/company_ai/artifacts/`.
- `RepoWriteTool` is intentionally simple and includes comments warning about repository write risk.
- `RunTestsTool` and `RunLintTool` execute local shell commands only.
- Web tools only perform outbound HTTP requests and do not execute downloaded content.
