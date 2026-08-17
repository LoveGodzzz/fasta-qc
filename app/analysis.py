from dataclasses import dataclass
from pathlib import Path

from Bio import SeqIO


ALLOWED_DNA_CHARS = set("ACGTN")


@dataclass
class SequenceQC:
    sequence_id: str
    length: int
    gc_percent: float
    n_count: int
    invalid_chars: str
    is_valid: bool


def analyze_sequence(sequence_id: str, sequence: str) -> SequenceQC:
    sequence = "".join(sequence.upper().split())
    length = len(sequence)

    gc_count = sequence.count("G") + sequence.count("C")
    n_count = sequence.count("N")
    invalid_chars = sorted(set(sequence) - ALLOWED_DNA_CHARS)

    gc_percent = round(gc_count / length * 100, 2) if length else 0.0

    return SequenceQC(
        sequence_id=sequence_id,
        length=length,
        gc_percent=gc_percent,
        n_count=n_count,
        invalid_chars="".join(invalid_chars),
        is_valid=length > 0 and not invalid_chars,
    )


def analyze_fasta(path: str | Path) -> list[SequenceQC]:
    fasta_path = Path(path)

    if not fasta_path.exists():
        raise FileNotFoundError(f"找不到文件：{fasta_path}")

    results = []

    for record in SeqIO.parse(fasta_path, "fasta"):
        result = analyze_sequence(
            sequence_id=record.id,
            sequence=str(record.seq),
        )
        results.append(result)

    if not results:
        raise ValueError("FASTA 文件中没有找到序列")

    return results