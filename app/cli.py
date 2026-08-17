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
        "invalid_chars",
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
                "invalid_chars": result.invalid_chars,
                "is_valid": result.is_valid,
            })

    print(f"\nCSV 报告已保存：{output}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="检查 DNA FASTA 文件的基本质量指标"
    )
    parser.add_argument("input", help="输入 FASTA 文件路径")
    parser.add_argument(
        "-o",
        "--output",
        help="输出 CSV 文件路径",
    )

    args = parser.parse_args()

    try:
        results = analyze_fasta(args.input)
    except (FileNotFoundError, ValueError) as error:
        print(f"错误：{error}", file=sys.stderr)
        return 1

    print("\nFASTA 质量检查结果")
    print("=" * 65)
    print(
        f"{'ID':<15}"
        f"{'长度':>8}"
        f"{'GC%':>10}"
        f"{'N数量':>10}"
        f"{'非法字符':>12}"
        f"{'结果':>10}"
    )
    print("-" * 65)

    for result in results:
        invalid = result.invalid_chars or "-"
        status = "通过" if result.is_valid else "失败"

        print(
            f"{result.sequence_id:<15}"
            f"{result.length:>8}"
            f"{result.gc_percent:>10.2f}"
            f"{result.n_count:>10}"
            f"{invalid:>12}"
            f"{status:>10}"
        )

    valid_count = sum(result.is_valid for result in results)

    print("-" * 65)
    print(f"序列总数：{len(results)}")
    print(f"通过数量：{valid_count}")
    print(f"失败数量：{len(results) - valid_count}")

    if args.output:
        save_csv(results, args.output)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())