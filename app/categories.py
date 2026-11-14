import re

# Match meaningful terms, not arbitrary substrings (for example, "mcp" inside
# another word). Generic words such as "integration" are intentionally omitted.
CATEGORY_PATTERNS = {
    "mcp": [r"\bmcp\b", r"model context protocol", r"mcp server"],
    "skills": [r"\bagent skills?\b", r"\bskills?\.md\b", r"\bskill registry\b"],
    "plugins": [r"\bplugins?\b", r"\bplugin system\b", r"\btool extensions?\b"],
    "frameworks": [r"\bagent frameworks?\b", r"\blangchain\b", r"\bautogen\b", r"\bcrewai\b", r"\bllamaindex\b", r"\bsemantic kernel\b"],
    "memory-rag": [r"\bagent memory\b", r"\bmemory store\b", r"\bRAG\b", r"\bretrieval augmented generation\b", r"\bvector database\b", r"\bvector store\b"],
    "tools": [r"\btool calling\b", r"\bfunction calling\b", r"\bagent tools?\b", r"\btool use\b"],
    "workflows": [r"\bagent workflows?\b", r"\borchestration\b", r"\bworkflow automation\b", r"\bmulti[- ]agent pipeline\b"],
}


def categorize(text: str) -> list[str]:
    haystack = str(text or "").lower()
    matches = []
    for category, patterns in CATEGORY_PATTERNS.items():
        if any(re.search(pattern, haystack, re.IGNORECASE) for pattern in patterns):
            matches.append(category)
    return matches or ["other"]
