from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .github_client import GitHubClient
from .analyzer import analyze
from .storage import get_scan, latest_repositories, list_scans, save_scan

app = FastAPI(title="AI Agent Ecosystem Scanner", version="0.2.0")
STATIC = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/", response_class=HTMLResponse)
async def home():
    return (Path(__file__).parent / "templates" / "index.html").read_text()


@app.get("/health")
async def health():
    return {"status": "ok", "repositories": len(latest_repositories())}


@app.post("/api/scan")
async def scan():
    if not settings.github_token:
        raise HTTPException(400, "Set GITHUB_TOKEN before scanning.")
    client = GitHubClient()
    try:
        items = await client.search(settings.scan_limit)
        results = []
        for item in items:
            readme = await client.readme(item["full_name"])
            repo = {
                "full_name": item["full_name"], "name": item.get("name", ""),
                "description": item.get("description") or "", "stars": item.get("stargazers_count", 0),
                "forks": item.get("forks_count", 0), "language": item.get("language"),
                "license": (item.get("license") or {}).get("spdx_id"),
                "topics": item.get("topics", []), "updated_at": item.get("updated_at"),
                "html_url": item.get("html_url"), "readme": readme,
            }
            repo.update(analyze(repo))
            repo.pop("readme", None)
            results.append(repo)
        run_id = save_scan(results)
        return {"scan_id": run_id, "scanned": len(results)}
    except Exception as exc:
        raise HTTPException(502, f"GitHub scan failed: {exc}") from exc


@app.get("/api/repos")
async def repos():
    return latest_repositories()


@app.get("/api/recommendations")
async def recommendations():
    return [r for r in latest_repositories() if r.get("score", 0) >= 20][:10]


@app.get("/api/scans")
async def scans(limit: int = Query(default=20, ge=1, le=100)):
    return list_scans(limit)


@app.get("/api/scans/{scan_id}")
async def scan_detail(scan_id: int):
    result = get_scan(scan_id)
    if result is None:
        raise HTTPException(404, "Scan not found")
    return result
