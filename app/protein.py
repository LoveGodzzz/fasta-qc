from dataclasses import dataclass
from pathlib import Path

from Bio import SeqIO


PROTEIN_ALLOWED_CHARS = set(
    "ACDEFGHIKLMNPQRSTVWYBXZJUO*"
)


@dataclass
class ProteinQC:
    sequence_id: str
    length: int
    invalid_chars: str
    failure_reasons: str
    is_valid: bool


def analyze_protein_sequence(
    sequence_id: str,
    sequence: str,
    min_length: int = 0,
) -> ProteinQC:
    sequence = "".join(sequence.upper().split())
    length = len(sequence)

    invalid_chars = sorted(
        set(sequence) - PROTEIN_ALLOWED_CHARS
    )

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

    return ProteinQC(
        sequence_id=sequence_id,
        length=length,
        invalid_chars="".join(invalid_chars),
        failure_reasons="；".join(failure_reasons),
        is_valid=len(failure_reasons) == 0,
    )

def analyze_protein_fasta(
    path: str | Path,
    min_length: int = 0,
) -> list[ProteinQC]:
    fasta_path = Path(path)

    if not fasta_path.exists():
        raise FileNotFoundError(
            f"找不到文件：{fasta_path}"
        )

    results = []

    for record in SeqIO.parse(
        fasta_path,
        "fasta",
    ):
        result = analyze_protein_sequence(
            sequence_id=record.id,
            sequence=str(record.seq),
            min_length=min_length,
        )
        results.append(result)

    if not results:
        raise ValueError(
            "FASTA 文件中没有找到蛋白质序列"
        )

    return results