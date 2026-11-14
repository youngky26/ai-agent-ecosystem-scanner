from app.publish import MAX_HISTORY, merge_history


def _src(ts, count=30):
    return {"scanned_at": ts, "count": count, "repositories": []}


def test_history_is_preserved_across_runs_even_when_db_scan_id_is_always_1():
    history, n1 = merge_history([], _src("2026-11-14T02:17:00+00:00"))
    history, n2 = merge_history(history, _src("2026-11-15T02:17:00+00:00"))
    assert (n1, n2) == (1, 2)
    assert [h["scan_id"] for h in history] == [1, 2]


def test_same_timestamp_is_not_duplicated():
    history, _ = merge_history([], _src("t1"))
    history, _ = merge_history(history, _src("t1"))
    assert len(history) == 1


def test_history_is_capped():
    history = []
    for i in range(MAX_HISTORY + 5):
        history, _ = merge_history(history, _src(f"t{i}"))
    assert len(history) == MAX_HISTORY
    assert history[-1]["scan_id"] == MAX_HISTORY + 5
