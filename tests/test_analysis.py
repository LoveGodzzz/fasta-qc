from pathlib import Path

import pytest

from app.analysis import analyze_fasta, analyze_sequence


def test_gc_percent() -> None:
    result = analyze_sequence("seq1", "GGCCAA")

    assert result.length == 6
    assert result.gc_percent == 66.67
    assert result.n_count == 0
    assert result.is_valid is True


def test_lowercase_and_n_count() -> None:
    result = analyze_sequence("seq2", "atnngc")

    assert result.length == 6
    assert result.gc_percent == 33.33
    assert result.n_count == 2
    assert result.is_valid is True


def test_invalid_character() -> None:
    result = analyze_sequence("seq3", "ATGCX")

    assert result.invalid_chars == "X"
    assert result.is_valid is False


def test_empty_sequence() -> None:
    result = analyze_sequence("empty", "")

    assert result.length == 0
    assert result.gc_percent == 0.0
    assert result.is_valid is False


def test_analyze_fasta(tmp_path: Path) -> None:
    fasta_file = tmp_path / "small.fasta"
    fasta_file.write_text(
        ">a\nATGC\n>b\nAANN\n",
        encoding="utf-8",
    )

    results = analyze_fasta(fasta_file)

    assert len(results) == 2
    assert results[0].sequence_id == "a"
    assert results[0].gc_percent == 50.0
    assert results[1].n_count == 2


def test_missing_file() -> None:
    with pytest.raises(FileNotFoundError):
        analyze_fasta("file-does-not-exist.fasta")


def test_empty_fasta(tmp_path: Path) -> None:
    empty_file = tmp_path / "empty.fasta"
    empty_file.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="没有找到序列"):
        analyze_fasta(empty_file)