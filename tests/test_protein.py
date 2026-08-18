from pathlib import Path

from app.protein import (
    analyze_protein_fasta,
    analyze_protein_sequence,
)


def test_valid_protein_sequence() -> None:
    result = analyze_protein_sequence(
        "protein1",
        "MKTLLLTLVVVTIVCLDLGY",
    )

    assert result.length == 20
    assert result.invalid_chars == ""
    assert result.failure_reasons == ""
    assert result.is_valid is True


def test_invalid_protein_sequence() -> None:
    result = analyze_protein_sequence(
        "bad",
        "MKTLL123",
    )

    assert result.invalid_chars == "123"
    assert "包含非法字符" in result.failure_reasons
    assert result.is_valid is False


def test_analyze_protein_fasta(
    tmp_path: Path,
) -> None:
    fasta_file = tmp_path / "proteins.fasta"

    fasta_file.write_text(
        ">valid\nMKTLLLTLVVV\n"
        ">short\nMKT\n",
        encoding="utf-8",
    )

    results = analyze_protein_fasta(
        fasta_file,
        min_length=5,
    )

    assert len(results) == 2
    assert results[0].sequence_id == "valid"
    assert results[0].is_valid is True

    assert results[1].sequence_id == "short"
    assert results[1].is_valid is False
    assert "长度小于要求" in results[1].failure_reasons