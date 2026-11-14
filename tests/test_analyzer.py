from app.analyzer import analyze
from app.categories import categorize


def test_category_matching_avoids_substrings():
    assert "mcp" not in categorize("this project uses a compact model")
    assert "mcp" in categorize("An MCP server for agents")


def test_scoring_is_bounded_and_explainable():
    result = analyze({
        "name": "Agent MCP",
        "description": "An MCP server and agent workflow",
        "stars": 1200,
        "forks": 100,
        "topics": ["mcp", "agents"],
        "license": "MIT",
        "updated_at": "2026-11-10T00:00:00Z",
        "readme": "# Agent\n" + ("documentation " * 300),
    })
    assert 0 <= result["score"] <= 100
    assert sum(result["score_breakdown"].values()) == result["score"]
    assert "mcp" in result["categories"]
    assert "workflows" in result["categories"]


def test_missing_metadata_does_not_crash():
    result = analyze({"name": "unknown", "stars": 0, "forks": 0})
    assert result["score"] == 0
    assert result["categories"] == ["other"]


def test_secret_findings_are_masked_and_placeholders_ignored():
    real = "ghp_" + "aB3dE5fG7hJ9kL1mN3pQ5rS7tU9vW1xY3zA5"
    readme = f"token {real} and sk-xxxxxxxxxxxxxxxxxxxxxxxx and sk-your-api-key-goes-here-123"
    result = analyze({"name": "x", "readme": readme})
    assert [f["type"] for f in result["secret_findings"]] == ["GitHub token"]
    assert result["secret_findings"][0]["evidence"] == "ghp_…"
