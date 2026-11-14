import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

from .config import settings
from .github_client import GitHubClient
from .pipeline import collect_repositories
from .storage import save_scan


async def main():
    if not settings.github_token:
        raise RuntimeError("GITHUB_TOKEN is required. Configure the workflow token or .env.")

    results = await collect_repositories(GitHubClient(), settings.scan_limit)
    scanned_at = datetime.now(timezone.utc)
    run_id = save_scan(results, scanned_at=scanned_at)
    output = {
        "scan_id": run_id,
        "scanned_at": scanned_at.isoformat(),
        "count": len(results),
        "repositories": results,
    }
    Path("scan-results.json").write_text(
        json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Scanned and analyzed {len(results)} repositories (scan id {run_id}).")
    for repo in results[:10]:
        print(f'{repo["score"]:3} | {repo["full_name"]} | {repo["stars"]} stars | {repo["html_url"]}')
    print("Full results saved to scan-results.json")


if __name__ == "__main__":
    asyncio.run(main())
