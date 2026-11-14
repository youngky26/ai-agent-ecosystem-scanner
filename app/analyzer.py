import re
from .categories import categorize

SECRET_PATTERNS = [
    ("GitHub token", re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}")),
    ("OpenAI key", re.compile(r"sk-[A-Za-z0-9_-]{20,}")),
    ("AWS access key", re.compile(r"AKIA[0-9A-Z]{16}")),
]

def analyze(repo: dict) -> dict:
    text = " ".join(str(repo.get(k, "")) for k in ("name", "description", "readme", "topics"))
    score = 0
    score += min(int(repo.get("stars", 0)) // 10, 25)
    score += min(int(repo.get("forks", 0)) // 5, 10)
    score += 15 if repo.get("readme") else 0
    score += 10 if repo.get("license") else 0
    score += 10 if repo.get("updated_at") else 0
    findings = []
    for label, pattern in SECRET_PATTERNS:
        for match in pattern.finditer(str(repo.get("readme", ""))):
            findings.append({"type": label, "evidence": match.group(0)[:4] + "…" + match.group(0)[-4:]})
    return {"categories": categorize(text), "score": min(score, 100), "secret_findings": findings}
