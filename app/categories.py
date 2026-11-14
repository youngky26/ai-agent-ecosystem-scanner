CATEGORIES = {
    "mcp": ["mcp", "model context protocol", "mcp server"],
    "skills": ["agent skill", "skills", "skill.md"],
    "plugins": ["plugin", "extension", "integration"],
    "frameworks": ["agent framework", "langchain", "autogen", "crewai", "llamaindex"],
    "memory-rag": ["memory", "rag", "vector", "retrieval", "knowledge base"],
    "tools": ["tool calling", "function calling", "agent tool", "sdk"],
    "workflows": ["workflow", "orchestration", "automation"],
}

def categorize(text: str) -> list[str]:
    haystack = text.lower()
    return [name for name, terms in CATEGORIES.items() if any(term in haystack for term in terms)] or ["other"]
