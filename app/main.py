import asyncio
import logging
import secrets
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .github_client import GitHubClient
from .pipeline import collect_repositories
from .storage import get_scan, latest_repositories, list_scans, save_scan

logger = logging.getLogger(__name__)
app = FastAPI(title="AI Agent Ecosystem Scanner", version="0.3.0")
STATIC = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/", response_class=HTMLResponse)
async def home():
    return (Path(__file__).parent / "templates" / "index.html").read_text()


@app.get("/health")
def health():
    return {"status": "ok", "repositories": len(latest_repositories())}


@app.post("/api/scan")
async def scan(x_scan_key: str = Header(default="", alias="X-Scan-Key")):
    if not settings.scan_api_key:
        raise HTTPException(503, "Admin scanning is disabled until SCAN_API_KEY is configured.")
    if not secrets.compare_digest(x_scan_key, settings.scan_api_key):
        raise HTTPException(401, "A valid admin scan key is required.")
    if not settings.github_token:
        raise HTTPException(400, "Set GITHUB_TOKEN before scanning.")
    try:
        results = await collect_repositories(GitHubClient(), settings.scan_limit)
        run_id = await asyncio.to_thread(save_scan, results)
        return {"scan_id": run_id, "scanned": len(results)}
    except Exception as exc:
        logger.exception("GitHub scan failed")
        raise HTTPException(502, "GitHub scan failed; see server logs for details.") from exc


@app.get("/api/repos")
def repos():
    return latest_repositories()


@app.get("/api/recommendations")
def recommendations():
    return [r for r in latest_repositories() if r.get("score", 0) >= 20][:10]


@app.get("/api/scans")
def scans(limit: int = Query(default=20, ge=1, le=100)):
    return list_scans(limit)


@app.get("/api/scans/{scan_id}")
def scan_detail(scan_id: int):
    result = get_scan(scan_id)
    if result is None:
        raise HTTPException(404, "Scan not found")
    return result
