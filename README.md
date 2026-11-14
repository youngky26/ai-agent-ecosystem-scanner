# AI Agent Ecosystem Scanner

A self-hosted dashboard for discovering and ranking public GitHub projects in the AI-agent ecosystem: MCP servers, agent frameworks, skills, plugins, tools, memory, RAG, and agent workflows.

## Features
- Seven targeted GitHub repository discovery queries.
- Metadata and README analysis with heuristic categorization.
- Explainable 0–100 score with component breakdown.
- Basic secret-pattern checks against README text only (not full repository security scanning).
- Persistent scan history through SQLite or PostgreSQL.
- Dashboard with latest repositories and scan history.
- Daily GitHub Actions scan and downloadable JSON artifact.
- Admin-key protection for scans triggered from the public dashboard.

## Deploy on Render

1. Push this repository to GitHub (already done).
2. Open [Render Blueprints](https://render.com/deploy) and select this repository. Render reads `render.yaml` and creates the web service.
3. Create a PostgreSQL database with a provider such as [Neon](https://neon.tech/) or Render Postgres. Use a persistent PostgreSQL database for production; the web service's local filesystem is not a durable database.
4. In the Render web service environment settings, set:
   - `DATABASE_URL`: the PostgreSQL connection URL from your database provider.
   - `GITHUB_TOKEN`: a GitHub token with public repository read access.
   - `SCAN_API_KEY`: Render generates a value from the blueprint; keep it private.
5. Deploy. Check the service's `/health` endpoint, then open the service URL.

The free web-service plan can sleep when idle and may take time to wake. Database provider pricing, free-tier limits, and retention vary; check them before creating a database. No paid database is created automatically by this blueprint.

## Share scan history with GitHub Actions

To write scheduled scan results into the same database as the deployed dashboard, add a GitHub Actions repository secret named `DATABASE_URL` containing the same PostgreSQL connection URL. The workflow already reads this secret. Without it, scheduled scan artifacts are still generated, but the workflow's temporary database is not shared with the web dashboard.

## Run locally
```bash
cp .env.example .env
# Set GITHUB_TOKEN and SCAN_API_KEY in .env
docker compose up --build
```
Open http://localhost:8000.

## API
- `GET /` dashboard
- `GET /health` health check
- `GET /api/repos` latest scan results
- `GET /api/recommendations` ranked recommendations
- `GET /api/scans` scan history
- `GET /api/scans/{scan_id}` one scan and its repositories
- `POST /api/scan` trigger a scan; requires the `X-Scan-Key` header

The scan endpoint returns HTTP 503 when `SCAN_API_KEY` is not configured and HTTP 401 for an invalid key. Never put the admin key in public source code or commit it to Git.

## Scoring model

The score is a heuristic ranking aid, not a quality or security certification. It combines popularity (20), community (10), freshness (20), metadata (15), documentation (15), and ecosystem relevance (20). The `score_breakdown` field exposes each component.

## Environment variables
- `GITHUB_TOKEN`: GitHub token with public repository read access.
- `DATABASE_URL`: SQLAlchemy URL; SQLite is suitable for local development, PostgreSQL for deployment.
- `SCAN_API_KEY`: secret required for dashboard-triggered scans.
- `SCAN_LIMIT`: maximum repositories to discover (default 30).
- `OPENAI_API_KEY`: reserved; OpenAI summaries are not implemented.

## Tests
Run `PYTHONPATH=. pytest -q`. CI runs tests and Python compilation on pushes and pull requests.

## Limitations
Scoring and categories are heuristic. Secret checks inspect README text only and are not a substitute for repository-wide secret scanning. Search results depend on GitHub Search API quotas and ranking. OpenAI summaries and dependency vulnerability scanning are not implemented.
