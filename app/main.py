from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from .config import settings
from .github_client import GitHubClient
from .analyzer import analyze

app = FastAPI(title="AI Agent Ecosystem Scanner", version="0.1.0")
STATIC = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC), name="static")
SCANNED: dict[str, dict] = {}

@app.get("/", response_class=HTMLResponse)
async def home():
    return (Path(__file__).parent / "templates" / "index.html").read_text()

@app.get("/health")
async def health():
    return {"status": "ok", "repositories": len(SCANNED)}

@app.post("/api/scan")
async def scan():
    if not settings.github_token:
        raise HTTPException(400, "Set GITHUB_TOKEN before scanning.")
    client = GitHubClient()
    try:
        items = await client.search(settings.scan_limit)
        for item in items:
            readme = await client.readme(item["full_name"])
            repo = {
                "full_name": item["full_name"], "name": item["name"],
                "description": item.get("description") or "", "stars": item.get("stargazers_count", 0),
                "forks": item.get("forks_count", 0), "language": item.get("language"),
                "license": (item.get("license") or {}).get("spdx_id"),
                "topics": item.get("topics", []), "updated_at": item.get("updated_at"),
                "html_url": item.get("html_url"), "readme": readme,
            }
            repo.update(analyze(repo))
            SCANNED[repo["full_name"]] = repo
        return {"scanned": len(items), "total": len(SCANNED)}
    except Exception as exc:
        raise HTTPException(502, f"GitHub scan failed: {exc}") from exc

@app.get("/api/repos")
async def repos():
    return sorted(SCANNED.values(), key=lambda r: r["score"], reverse=True)

@app.get("/api/recommendations")
async def recommendations():
    return [r for r in sorted(SCANNED.values(), key=lambda r: r["score"], reverse=True) if r["score"] >= 20][:10]
