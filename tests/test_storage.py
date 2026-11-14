from datetime import datetime, timezone

from sqlalchemy import create_engine

from app.storage import get_scan, latest_repositories, list_scans, save_scan


def test_scan_history_persists_and_can_be_retrieved():
    engine = create_engine("sqlite:///:memory:")
    repositories = [
        {"full_name": "sample/agent", "score": 42, "categories": ["mcp"]}
    ]
    scan_id = save_scan(
        repositories,
        scanned_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        db_engine=engine,
    )

    assert latest_repositories(engine) == repositories
    assert get_scan(scan_id, engine)["repositories"] == repositories
    assert list_scans(1, engine)[0]["count"] == 1


def test_empty_database_returns_empty_history():
    engine = create_engine("sqlite:///:memory:")
    assert latest_repositories(engine) == []
    assert list_scans(db_engine=engine) == []
