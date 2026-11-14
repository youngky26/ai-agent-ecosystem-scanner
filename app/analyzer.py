import math
import re
from datetime import datetime, timezone

from .categories import categorize

SECRET_PATTERNS = [
    ("GitHub token", re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}")),
    ("OpenAI key", re.compile(r"sk-[A-Za-z0-9_-]{20,}")),
    ("AWS access key", re.compile(r"AKIA[0-9A-Z]{16}")),
]


def _freshness_score(updated_at: str | None) -> int:
    if not updated_at:
        return 0
    try:
        updated = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
        if updated.tzinfo is None:
            updated = updated.replace(tzinfo=timezone.utc)
        age_days = max(0, (datetime.now(timezone.utc) - updated).days)
    except (TypeError, ValueError):
        return 0
    if age_days <= 30:
        return 20
    if age_days <= 90:
        return 16
    if age_days <= 180:
        return 12
    if age_days <= 365:
        return 7
    if age_days <= 730:
        return 3
    return 0


def _score(repo: dict, categories: list[str]) -> tuple[int, dict]:
    stars = max(0, int(repo.get("stars") or 0))
    forks = max(0, int(repo.get("forks") or 0))
    popularity = min(20, round(math.log10(stars + 1) * 4))
    fork_ratio = forks / max(stars, 1)
    community = min(10, round(min(fork_ratio, 0.5) * 20))
    freshness = _freshness_score(repo.get("updated_at"))
    metadata = (5 if repo.get("description") else 0) + (5 if repo.get("topics") else 0) + (5 if repo.get("license") else 0)
    readme_length = len(str(repo.get("readme") or "").strip())
    documentation = 0 if readme_length == 0 else 5 if readme_length < 500 else 10 if readme_length < 2000 else 15
    relevance = min(20, len(categories) * 7) if categories != ["other"] else 0
    breakdown = {
        "popularity": popularity,
        "community": community,
        "freshness": freshness,
        "metadata": metadata,
        "documentation": documentation,
        "ecosystem_relevance": relevance,
    }
    return min(100, sum(breakdown.values())), breakdown


def analyze(repo: dict) -> dict:
    source_text = " ".join(
        str(repo.get(key, "") or "")
        for key in ("name", "description", "readme", "topics")
    )
    categories = categorize(source_text)
    score, breakdown = _score(repo, categories)

    findings = []
    readme = str(repo.get("readme", "") or "")
    for label, pattern in SECRET_PATTERNS:
        for match in pattern.finditer(readme):
            value = match.group(0)
            findings.append({
                "type": label,
                "evidence": value[:4] + "…" + value[-4:],
            })

    return {
        "categories": categories,
        "score": score,
        "score_breakdown": breakdown,
        "secret_findings": findings,
    }
