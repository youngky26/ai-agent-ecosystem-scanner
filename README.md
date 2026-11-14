# AI Agent Ecosystem Scanner

A self-hosted MVP for discovering and ranking public GitHub projects in the AI-agent ecosystem: MCP servers, agent frameworks, skills, plugins, tools, memory, RAG, and agent workflows.

## Implemented features
- GitHub repository discovery using seven targeted search queries.
- Repository metadata and README collection.
- More precise keyword-based categorization (still heuristic).
- Explainable relevance score with a component breakdown.
- Basic secret-pattern checks against README text, with evidence redacted.
- FastAPI dashboard and JSON API for scans started from the running web app.
- GitHub Actions scan on each push to `main`, daily at 02:17 UTC, or manually.
- Scan results exported as a downloadable GitHub Actions artifact (`scan-results.json`).

## Scoring model

The 0–100 score is a heuristic ranking aid, not a quality or security certification.

| Component | Maximum | What it measures |
|---|---:|---|
| Popularity | 20 | Log-scaled GitHub stars |
| Community | 10 | Fork-to-star ratio, capped |
| Freshness | 20 | How recently the repository was updated |
| Metadata | 15 | Description, topics, and license presence |
| Documentation | 15 | README presence and length bands |
| Ecosystem relevance | 20 | Number of matched ecosystem categories |

Every result includes `score_breakdown` so the score can be inspected. A higher score does not guarantee code quality, maintenance quality, or safety.

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
The scanner runs automatically on pushes to `main`, daily, and through manual workflow dispatch. It uses the workflow's built-in GitHub token. After a successful run, download the `ai-agent-ecosystem-scan-results` artifact from the run.

## API
- `GET /` dashboard
- `GET /health` health check
- `GET /api/repos` scanned repositories held in the running app's memory
- `GET /api/recommendations` ranked recommendations
- `POST /api/scan` trigger a scan (protect this endpoint before exposing publicly)

## Tests
Run `pytest -q`. CI runs unit tests and Python compilation on pushes and pull requests.

## Current limitations
This is an early MVP. The web app currently keeps scan results in memory, so results are lost when the process restarts. GitHub Actions results are downloadable artifacts for 30 days; they are not synchronized into the web dashboard or a persistent database. Categorization, scoring, and secret checks remain heuristic. Secret checks inspect README text only and are not a substitute for repository-wide secret scanning. OpenAI summaries and dependency vulnerability scanning are not implemented yet.
