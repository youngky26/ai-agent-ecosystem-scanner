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

    async def search(self, limit: int = 30) -> list[dict]:
        results = {}
        # Reserve room for every query so the first broad MCP search cannot
        # consume the entire scan limit before other ecosystem areas are checked.
        per_query = max(3, min(10, (limit + len(QUERIES) - 1) // len(QUERIES)))
        async with httpx.AsyncClient(timeout=30) as client:
            for query in QUERIES:
                response = await client.get(
                    f"{BASE}/search/repositories",
                    params={
                        "q": query + " is:public",
                        "sort": "updated",
                        "per_page": per_query,
                    },
                    headers=self.headers,
                )
                response.raise_for_status()
                for item in response.json().get("items", []):
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
            import base64
            return base64.b64decode(data.get("content", "")).decode("utf-8", "replace")
