import asyncio

from .analyzer import analyze
from .github_client import GitHubClient


def _to_repo(item: dict, readme: str) -> dict:
    return {
        "full_name": item["full_name"], "name": item.get("name", ""),
        "description": item.get("description") or "", "stars": item.get("stargazers_count", 0),
        "forks": item.get("forks_count", 0), "language": item.get("language"),
        "license": (item.get("license") or {}).get("spdx_id"),
        "topics": item.get("topics", []), "updated_at": item.get("updated_at"),
        "html_url": item.get("html_url"), "readme": readme,
    }


async def collect_repositories(client: GitHubClient, limit: int, concurrency: int = 5) -> list[dict]:
    items = await client.search(limit)
    sem = asyncio.Semaphore(concurrency)

    async def build(item: dict) -> dict:
        async with sem:
            readme = await client.readme(item["full_name"])
        repo = _to_repo(item, readme)
        repo.update(analyze(repo))
        repo.pop("readme", None)
        return repo

    results = await asyncio.gather(*(build(i) for i in items))
    return sorted(results, key=lambda r: r["score"], reverse=True)
