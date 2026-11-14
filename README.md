# AI Agent Ecosystem Scanner

A self-hosted MVP for discovering and ranking public GitHub projects in the AI-agent ecosystem: MCP servers, agent frameworks, skills, plugins, tools, memory, RAG, and agent workflows.

## Implemented features
- GitHub repository discovery using seven targeted search queries.
- Repository metadata and README collection.
- More precise keyword-based categorization (still heuristic).
- Explainable relevance score with a component breakdown.
- Basic secret-pattern checks against README text, with evidence redacted.
- FastAPI dashboard and JSON API.
- Persistent scan history using SQLite by default; PostgreSQL is supported through `DATABASE_URL`.
- Daily GitHub Actions scan and downloadable JSON artifact.

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
Open http://localhost:8000. Docker Compose mounts a persistent volume at `/app/data` for the SQLite database.

## Environment
- `GITHUB_TOKEN`: GitHub token with public repository read access (recommended).
- `SCAN_LIMIT`: maximum repositories to discover (default 30).
- `DATABASE_URL`: SQLAlchemy database URL. Defaults to SQLite; PostgreSQL is supported.
- `OPENAI_API_KEY`: reserved for future extensions; not currently used.

## API
- `GET /` dashboard
- `GET /health` health check
- `GET /api/repos` repositories from the latest stored scan
- `GET /api/recommendations` ranked recommendations from the latest scan
- `GET /api/scans` recent scan history
- `GET /api/scans/{scan_id}` one scan and its repositories
- `POST /api/scan` trigger and persist a scan (protect this endpoint before exposing publicly)

## Scheduled scans and shared history
GitHub Actions runs daily at 02:17 UTC or manually. Each run uploads `scan-results.json` as an artifact for 30 days. The runner's local SQLite file is temporary. To make scheduled results appear in the same database as a deployed web app, configure the same PostgreSQL `DATABASE_URL` as a GitHub Actions repository secret named `DATABASE_URL` and as the web app environment variable. Without that shared database configuration, scheduled scan artifacts and the web app's database remain separate.

## Tests
Run `PYTHONPATH=. pytest -q`. CI runs tests and Python compilation on pushes and pull requests.

## Current limitations
Categorization, scoring, and secret checks remain heuristic. Secret checks inspect README text only and are not a substitute for repository-wide secret scanning. Search results depend on GitHub Search API limits and query ranking. OpenAI summaries and dependency vulnerability scanning are not implemented yet.
