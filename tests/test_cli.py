import json
from pathlib import Path

from app.analysis import analyze_fasta, analyze_sequence
from app.cli import save_filtered_fasta, save_json


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
    
def test_save_filtered_fasta(tmp_path: Path) -> None:
    input_file = tmp_path / "input.fasta"
    output_file = tmp_path / "passed.fasta"

    input_file.write_text(
        ">good\nATGC\n>bad\nATGX\n",
        encoding="utf-8",
    )

    results = analyze_fasta(input_file)

    save_filtered_fasta(
        str(input_file),
        results,
        str(output_file),
    )

    output_text = output_file.read_text(
        encoding="utf-8"
    )

    assert ">good" in output_text
    assert "ATGC" in output_text
    assert ">bad" not in output_text
    assert "ATGX" not in output_text