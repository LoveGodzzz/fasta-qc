import json
from pathlib import Path

from app.analysis import analyze_sequence
from app.cli import save_json


def test_save_json(tmp_path: Path) -> None:
    output_file = tmp_path / "report.json"

    results = [
        analyze_sequence("seq1", "ATGC"),
        analyze_sequence("bad", "ATGX"),
    ]

    save_json(results, str(output_file))

    data = json.loads(
        output_file.read_text(encoding="utf-8")
    )

    assert len(data) == 2

    assert data[0]["sequence_id"] == "seq1"
    assert data[0]["gc_percent"] == 50.0
    assert data[0]["is_valid"] is True

    assert data[1]["sequence_id"] == "bad"
    assert data[1]["invalid_chars"] == "X"
    assert data[1]["is_valid"] is False