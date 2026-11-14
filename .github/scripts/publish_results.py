import json
from pathlib import Path

source = json.loads(Path("scan-results.json").read_text(encoding="utf-8"))
data_dir = Path("site/data")
data_dir.mkdir(parents=True, exist_ok=True)
(data_dir / "latest.json").write_text(
    json.dumps(source, ensure_ascii=False, indent=2), encoding="utf-8"
)
history_path = data_dir / "history.json"
history = json.loads(history_path.read_text(encoding="utf-8")) if history_path.exists() else []
entry = {
    "scan_id": source.get("scan_id"),
    "scanned_at": source.get("scanned_at"),
    "count": source.get("count", len(source.get("repositories", []))),
}
history = [item for item in history if item.get("scan_id") != entry["scan_id"]]
history.append(entry)
history = history[-60:]
history_path.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Published {entry['count']} repositories; retained {len(history)} scan records.")
