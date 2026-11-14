# AI Agent Ecosystem Scanner

A self-hosted MVP for discovering and ranking public GitHub projects in the AI-agent ecosystem: MCP servers, agent frameworks, skills, plugins, tools, memory, RAG, and integrations.

## Implemented features
- GitHub repository discovery using targeted search queries.
- Repository metadata and README collection.
- Heuristic categorization and relevance scoring.
- Basic secret-pattern checks against README text, with evidence redacted.
- FastAPI dashboard and JSON API for scans started from the running web app.
- GitHub Actions scan on each push to `main`, daily at 02:17 UTC, or manually.
- Scan results exported as a downloadable GitHub Actions artifact (`scan-results.json`).

## Run locally
```bash
cp .env.example .env
# Set GITHUB_TOKEN in .env
docker compose up --build
```
Open http://localhost:8000.

## Environment
- `GITHUB_TOKEN`: GitHub token with public repository read access (recommended).
- `SCAN_LIMIT`: maximum repositories to discover (default 30).
- `DATABASE_URL` and `OPENAI_API_KEY`: reserved for future extensions; they are not currently used by the scanner.

## GitHub Actions
The scanner runs automatically on pushes to `main`, daily, and through manual workflow dispatch. It uses the workflow's built-in GitHub token. After a successful run, open **Actions**, select **Daily ecosystem scan**, open the latest run, and download the `ai-agent-ecosystem-scan-results` artifact.

## API
- `GET /` dashboard
- `GET /health` health check
- `GET /api/repos` scanned repositories held in the running app's memory
- `GET /api/recommendations` ranked recommendations
- `POST /api/scan` trigger a scan (protect this endpoint before exposing publicly)

## Current limitations
This is an early MVP. The web app currently keeps scan results in memory, so results are lost when the process restarts. GitHub Actions results are available as a downloadable artifact for 30 days; they are not yet synchronized into the web dashboard or a persistent database. Categorization, scoring, and secret checks are heuristic, not a substitute for dedicated security scanning. OpenAI summaries and dependency vulnerability scanning are not implemented yet.
