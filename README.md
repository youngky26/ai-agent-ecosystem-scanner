# AI Agent Ecosystem Scanner

A GitHub Actions-powered scanner and static dashboard for discovering and ranking public GitHub projects in the AI-agent ecosystem: MCP servers, agent frameworks, skills, plugins, tools, memory, RAG, and agent workflows.

## Live dashboard

After enabling GitHub Pages with **GitHub Actions** as the build and deployment source, the dashboard will be published at:

`https://youngky26.github.io/ai-agent-ecosystem-scanner/`

## Features

- Seven targeted GitHub repository discovery queries.
- Metadata and README analysis with heuristic categorization.
- Explainable 0–100 score with component breakdown.
- Basic secret-pattern checks against README text only (not full repository security scanning).
- Daily scan using GitHub Actions (02:17 UTC / 09:17 WIB).
- Static dashboard hosted by GitHub Pages; no external server or payment card required.
- Search and category filters, latest scan summary, and up to 60 scan-history entries.
- Manual scan via the Actions workflow's **Run workflow** button.

## Enable GitHub Pages (one-time setup)

1. Open this repository on GitHub.
2. Go to **Settings → Pages**.
3. Under **Build and deployment → Source**, select **GitHub Actions**.
4. Save. The next successful workflow run publishes the site.

## Run a scan manually

1. Open the **Actions** tab in this repository.
2. Select **Daily ecosystem scan and GitHub Pages deploy**.
3. Click **Run workflow**, choose the `main` branch, then confirm.
4. Wait for the workflow to finish successfully. The dashboard is deployed automatically.

The scheduled scan runs daily. GitHub Actions uses its built-in `GITHUB_TOKEN`; no personal access token, database URL, Render service, or admin scan key is needed.

## Run locally

```bash
pip install -r requirements.txt
# Set GITHUB_TOKEN in your environment if you want to scan locally
python -m app.scan
```

The FastAPI app and local SQLite storage remain available for local development, but the public GitHub Pages dashboard is static and read-only. Scan data is published from `scan-results.json` into `site/data/`.

## Scoring model

The score is a heuristic ranking aid, not a quality or security certification. It combines popularity (20), community (10), freshness (20), metadata (15), documentation (15), and ecosystem relevance (20). The `score_breakdown` field exposes each component.

## Limitations

Scoring and categories are heuristic. Secret checks inspect README text only and are not a substitute for repository-wide secret scanning. Search results depend on GitHub Search API quotas and ranking. OpenAI summaries and dependency vulnerability scanning are not implemented. The Pages dashboard is read-only; starting a scan is done from GitHub Actions.
