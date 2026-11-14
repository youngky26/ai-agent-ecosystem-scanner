"""Publish scan results into the static dashboard data (site/data)."""
import json
from pathlib import Path

MAX_HISTORY = 60


def merge_history(history: list[dict], source: dict) -> tuple[list[dict], int]:
    """Append this scan to history and return (history, run_number).

    The scan database is recreated on every CI run, so the database scan_id is
    always 1. History therefore uses its own monotonically increasing number and
    de-duplicates by timestamp, so earlier entries are never wiped.
    """
    scanned_at = source.get("scanned_at")
    history = [item for item in history if item.get("scanned_at") != scanned_at]
    run_number = max((int(item.get("scan_id") or 0) for item in history), default=0) + 1
    history.append({
        "scan_id": run_number,
        "scanned_at": scanned_at,
        "count": source.get("count", len(source.get("repositories", []))),
    })
    return history[-MAX_HISTORY:], run_number


def publish(source_path: str = "scan-results.json", data_dir: str = "site/data") -> None:
    source = json.loads(Path(source_path).read_text(encoding="utf-8"))
    out = Path(data_dir)
    out.mkdir(parents=True, exist_ok=True)

    history_path = out / "history.json"
    history = json.loads(history_path.read_text(encoding="utf-8")) if history_path.exists() else []
    history, run_number = merge_history(history, source)
    source["scan_id"] = run_number

    (out / "latest.json").write_text(json.dumps(source, ensure_ascii=False, indent=2), encoding="utf-8")
    history_path.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Published {source.get('count')} repositories; retained {len(history)} scan records.")


if __name__ == "__main__":
    publish()
