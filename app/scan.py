import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

from .analyzer import analyze
from .config import settings
from .github_client import GitHubClient


async def main():
    if not settings.github_token:
        raise RuntimeError("GITHUB_TOKEN is required. Configure the workflow token or .env.")

    client = GitHubClient()
    items = await client.search(settings.scan_limit)
    results = []

    for item in items:
        full_name = item["full_name"]
        readme = await client.readme(full_name)
        repo = {
            "full_name": full_name,
            "name": item.get("name", ""),
            "description": item.get("description") or "",
            "stars": item.get("stargazers_count", 0),
            "forks": item.get("forks_count", 0),
            "language": item.get("language"),
            "license": (item.get("license") or {}).get("spdx_id"),
            "topics": item.get("topics", []),
            "updated_at": item.get("updated_at"),
            "html_url": item.get("html_url"),
            "readme": readme,
        }
        repo.update(analyze(repo))
        repo.pop("readme", None)
        results.append(repo)

    results.sort(key=lambda item: item["score"], reverse=True)
    output = {
        "scanned_at": datetime.now(timezone.utc).isoformat(),
        "count": len(results),
        "repositories": results,
    }
    Path("scan-results.json").write_text(
        json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"Scanned and analyzed {len(results)} repositories.")
    for repo in results[:10]:
        print(f'{repo["score"]:3} | {repo["full_name"]} | {repo["stars"]} stars | {repo["html_url"]}')
    print("Full results saved to scan-results.json")


if __name__ == "__main__":
    asyncio.run(main())
