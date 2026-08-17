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
        

def test_min_length_threshold() -> None:
    result = analyze_sequence(
        "short",
        "ATGC",
        min_length=5,
    )

    assert result.length == 4
    assert result.is_valid is False
    assert "长度小于要求：4 < 5" in result.failure_reasons


def test_max_n_percent_threshold() -> None:
    result = analyze_sequence(
        "many_n",
        "ATNNGC",
        max_n_percent=20,
    )

    assert result.n_count == 2
    assert result.n_percent == 33.33
    assert result.is_valid is False
    assert "N 比例超过要求" in result.failure_reasons


def test_analyze_fasta_applies_thresholds(
    tmp_path: Path,
) -> None:
    fasta_file = tmp_path / "thresholds.fasta"
    fasta_file.write_text(
        ">short\nATGC\n"
        ">many_n\nATNNGC\n",
        encoding="utf-8",
    )

    results = analyze_fasta(
        fasta_file,
        min_length=5,
        max_n_percent=20,
    )

    assert len(results) == 2

    assert results[0].sequence_id == "short"
    assert results[0].is_valid is False
    assert "长度小于要求" in results[0].failure_reasons

    assert results[1].sequence_id == "many_n"
    assert results[1].is_valid is False
    assert "N 比例超过要求" in results[1].failure_reasons
    
    
def test_min_gc_threshold() -> None:
    result = analyze_sequence(
        "low_gc",
        "AAAA",
        min_gc_percent=40,
    )

    assert result.gc_percent == 0.0
    assert result.is_valid is False
    assert "GC 比例低于要求" in result.failure_reasons


def test_max_gc_threshold() -> None:
    result = analyze_sequence(
        "high_gc",
        "GGGG",
        max_gc_percent=60,
    )

    assert result.gc_percent == 100.0
    assert result.is_valid is False
    assert "GC 比例超过要求" in result.failure_reasons


def test_gc_boundary_values_pass() -> None:
    result = analyze_sequence(
        "boundary",
        "ATGC",
        min_gc_percent=50,
        max_gc_percent=50,
    )

    assert result.gc_percent == 50.0
    assert result.failure_reasons == ""
    assert result.is_valid is True
    
def test_iupac_ambiguous_bases_are_allowed() -> None:
    result = analyze_sequence(
        "iupac",
        "ACGTRYSWKMBDHVN",
    )

    assert result.length == 15
    assert result.n_count == 1
    assert result.invalid_chars == ""
    assert result.failure_reasons == ""
    assert result.is_valid is True


def test_duplicate_sequence_ids_fail(tmp_path: Path) -> None:
    fasta_file = tmp_path / "duplicate.fasta"
    fasta_file.write_text(
        ">same\nATGC\n>same\nGGCC\n>unique\nAATT\n",
        encoding="utf-8",
    )

    results = analyze_fasta(fasta_file)

    assert len(results) == 3

    assert results[0].is_valid is False
    assert "序列 ID 重复：same" in results[0].failure_reasons

    assert results[1].is_valid is False
    assert "序列 ID 重复：same" in results[1].failure_reasons

    assert results[2].is_valid is True