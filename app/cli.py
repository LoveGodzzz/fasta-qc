import argparse
import csv
import sys
from pathlib import Path

from app.analysis import analyze_fasta


def save_csv(results: list, output_path: str) -> None:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "sequence_id",
        "length",
        "gc_percent",
        "n_count",
        "n_percent",
        "invalid_chars",
        "failure_reasons",
        "is_valid",
    ]

    with output.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for result in results:
            writer.writerow({
                "sequence_id": result.sequence_id,
                "length": result.length,
                "gc_percent": result.gc_percent,
                "n_count": result.n_count,
                "n_percent": result.n_percent,
                "invalid_chars": result.invalid_chars,
                "failure_reasons": result.failure_reasons,
                "is_valid": result.is_valid,
            })

    print(f"\nCSV 报告已保存：{output}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="检查 DNA FASTA 文件的基本质量指标"
    )

    parser.add_argument(
        "input",
        help="输入 FASTA 文件路径",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="输出 CSV 文件路径",
    )
    parser.add_argument(
        "--min-length",
        type=int,
        default=0,
        help="允许的最短序列长度，默认不限制",
    )
    parser.add_argument(
        "--max-n-percent",
        type=float,
        default=100.0,
        help="允许的最大 N 比例，默认 100",
    )

    args = parser.parse_args()

    if args.min_length < 0:
        parser.error("--min-length 不能小于 0")

    if not 0 <= args.max_n_percent <= 100:
        parser.error("--max-n-percent 必须在 0 到 100 之间")

    try:
        results = analyze_fasta(
            args.input,
            min_length=args.min_length,
            max_n_percent=args.max_n_percent,
        )
    except (FileNotFoundError, ValueError) as error:
        print(f"错误：{error}", file=sys.stderr)
        return 1

    print("\nFASTA 质量检查结果")
    print("=" * 100)
    print(f"最短长度要求：{args.min_length}")
    print(f"最大 N 比例：{args.max_n_percent}%")
    print("-" * 100)

    print(
        f"{'ID':<15}"
        f"{'长度':>8}"
        f"{'GC%':>9}"
        f"{'N':>7}"
        f"{'N%':>9}"
        f"{'结果':>9}"
        f"  失败原因"
    )
    print("-" * 100)

    for result in results:
        status = "PASS" if result.is_valid else "FAIL"
        reason = result.failure_reasons or "-"

        print(
            f"{result.sequence_id:<15}"
            f"{result.length:>8}"
            f"{result.gc_percent:>9.2f}"
            f"{result.n_count:>7}"
            f"{result.n_percent:>9.2f}"
            f"{status:>9}"
            f"  {reason}"
        )

    valid_count = sum(result.is_valid for result in results)

    print("-" * 100)
    print(f"序列总数：{len(results)}")
    print(f"通过数量：{valid_count}")
    print(f"失败数量：{len(results) - valid_count}")

    if args.output:
        save_csv(results, args.output)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())