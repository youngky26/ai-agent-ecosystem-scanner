import asyncio
import base64
import time

import httpx
from .config import settings

BASE = "https://api.github.com"
QUERIES = [
    '"MCP server" AI',
    '"AI agent" skills',
    '"AI agent" plugins',
    '"agent framework" LLM',
    '"agent memory" OR RAG',
    '"agent tools" SDK',
    '"agent workflow" orchestration',
]


class GitHubClient:
    def __init__(self):
        self.headers = {"Accept": "application/vnd.github+json"}
        if settings.github_token:
            self.headers["Authorization"] = f"Bearer {settings.github_token}"

    async def _search_query(self, client: httpx.AsyncClient, query: str, per_page: int):
        response = await client.get(
            f"{BASE}/search/repositories",
            params={"q": query + " is:public", "sort": "updated", "per_page": per_page},
            headers=self.headers,
        )
        if response.status_code == 403 and response.headers.get("X-RateLimit-Remaining") == "0":
            reset = int(response.headers.get("X-RateLimit-Reset", "0") or 0)
            wait_seconds = max(1, reset - int(time.time()) + 1)
            if wait_seconds <= 90:
                await asyncio.sleep(wait_seconds)
                response = await client.get(
                    f"{BASE}/search/repositories",
                    params={"q": query + " is:public", "sort": "updated", "per_page": per_page},
                    headers=self.headers,
                )
            else:
                raise RuntimeError(
                    f"GitHub Search API rate limit exhausted; retry after {wait_seconds} seconds."
                )
        if response.status_code == 403:
            raise RuntimeError(
                "GitHub Search API returned 403. Check token permissions and API rate limits: "
                + response.text[:300]
            )
        response.raise_for_status()
        return response.json().get("items", [])

    async def search(self, limit: int = 30) -> list[dict]:
        results = {}
        per_query = max(3, min(10, (limit + len(QUERIES) - 1) // len(QUERIES)))
        async with httpx.AsyncClient(timeout=30) as client:
            for query in QUERIES:
                items = await self._search_query(client, query, per_query)
                for item in items:
                    results[item["full_name"]] = item
                if len(results) >= limit:
                    break
        return list(results.values())[:limit]

    async def readme(self, full_name: str) -> str:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                f"{BASE}/repos/{full_name}/readme", headers=self.headers
            )
            if response.status_code != 200:
                return ""
            data = response.json()
            return base64.b64decode(data.get("content", "")).decode("utf-8", "replace")
