from dataclasses import dataclass
from pathlib import Path

from Bio import SeqIO


ALLOWED_DNA_CHARS = set("ACGTRYSWKMBDHVN")


@dataclass
class SequenceQC:
    sequence_id: str
    length: int
    gc_percent: float
    n_count: int
    n_percent: float
    invalid_chars: str
    failure_reasons: str
    is_valid: bool


def analyze_sequence(
    sequence_id: str,
    sequence: str,
    min_length: int = 0,
    max_n_percent: float = 100.0,
    min_gc_percent: float = 0.0,
    max_gc_percent: float = 100.0,
) -> SequenceQC:
    sequence = "".join(sequence.upper().split())
    length = len(sequence)

    gc_count = sequence.count("G") + sequence.count("C")
    n_count = sequence.count("N")
    invalid_chars = sorted(set(sequence) - ALLOWED_DNA_CHARS)

    gc_percent = round(gc_count / length * 100, 2) if length else 0.0
    n_percent = round(n_count / length * 100, 2) if length else 0.0

    failure_reasons = []

    if length == 0:
        failure_reasons.append("空序列")

    if invalid_chars:
        failure_reasons.append(
            f"包含非法字符：{''.join(invalid_chars)}"
        )

    if length < min_length:
        failure_reasons.append(
            f"长度小于要求：{length} < {min_length}"
        )

    if n_percent > max_n_percent:
        failure_reasons.append(
            f"N 比例超过要求：{n_percent}% > {max_n_percent}%"
        )
    
    if gc_percent < min_gc_percent:
        failure_reasons.append(
        f"GC 比例低于要求：{gc_percent}% < {min_gc_percent}%"
    )
    
    if gc_percent > max_gc_percent:
        failure_reasons.append(
        f"GC 比例超过要求：{gc_percent}% > {max_gc_percent}%"
    )
    
    return SequenceQC(
        sequence_id=sequence_id,
        length=length,
        gc_percent=gc_percent,
        n_count=n_count,
        n_percent=n_percent,
        invalid_chars="".join(invalid_chars),
        failure_reasons="；".join(failure_reasons),
        is_valid=len(failure_reasons) == 0,
    )


def analyze_fasta(
    path: str | Path,
    min_length: int = 0,
    max_n_percent: float = 100.0,
    min_gc_percent: float = 0.0,
    max_gc_percent: float = 100.0,
) -> list[SequenceQC]:
    fasta_path = Path(path)

    if not fasta_path.exists():
        raise FileNotFoundError(f"找不到文件：{fasta_path}")

    results = []

    for record in SeqIO.parse(fasta_path, "fasta"):
        result = analyze_sequence(
            sequence_id=record.id,
            sequence=str(record.seq),
            min_length=min_length,
            max_n_percent=max_n_percent,
            min_gc_percent=min_gc_percent,
            max_gc_percent=max_gc_percent,
)
        results.append(result)

    if not results:
        raise ValueError("FASTA 文件中没有找到序列")

    return results