import asyncio
from .github_client import GitHubClient
from .config import settings

async def main():
    client = GitHubClient()
    repos = await client.search(settings.scan_limit)
    print(f"Discovered {len(repos)} repositories")
    for repo in repos:
        print(repo["full_name"], repo.get("stargazers_count", 0), repo.get("html_url"))

if __name__ == "__main__":
    asyncio.run(main())
