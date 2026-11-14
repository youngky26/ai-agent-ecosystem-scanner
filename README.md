# AI Agent Ecosystem Scanner

A self-hosted intelligence scanner for public GitHub projects in the AI-agent ecosystem: MCP servers, agent frameworks, skills, plugins, tools, memory, RAG, and integrations.

## Features
- GitHub repository discovery using targeted search queries.
- Repository metadata, README, topics, language, license and activity collection.
- Heuristic categorization and relevance/quality scoring.
- Optional OpenAI summaries (deterministic fallback when no API key is configured).
- Basic secret-pattern detection with redacted evidence.
- FastAPI dashboard and JSON API.
- SQLite for local use; PostgreSQL supported for persistent deployments.
- Daily GitHub Actions scan and manual workflow dispatch.

## Run locally
```bash
cp .env.example .env
# Set GITHUB_TOKEN in .env
docker compose up --build
```
Open http://localhost:8000.

## Environment
- `GITHUB_TOKEN`: GitHub token with public repository read access (recommended).
- `DATABASE_URL`: defaults to SQLite; use PostgreSQL for hosted deployments.
- `OPENAI_API_KEY`: optional summaries.
- `OPENAI_MODEL`: optional model override.

## GitHub Actions
Add repository secrets `GITHUB_TOKEN` (or use the built-in token where permitted), `DATABASE_URL` and optionally `OPENAI_API_KEY`. The hosted runner filesystem is ephemeral; use PostgreSQL for data that must persist between scheduled runs.

## API
- `GET /` dashboard
- `GET /health` health check
- `GET /api/repos` scanned repositories
- `GET /api/recommendations` ranked recommendations
- `POST /api/scan` trigger a scan (protect this endpoint before exposing publicly)

## Scope
This is an extensible MVP. Security checks are heuristic and are not a substitute for dedicated SAST, dependency, or secret-scanning products. Dependency advisory checks should be treated as best-effort.
