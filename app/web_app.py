import csv
import json
import os
import tempfile
from io import StringIO
from pathlib import Path

import streamlit as st
from Bio import SeqIO

from app.analysis import analyze_fasta
from app.protein import analyze_protein_fasta


st.set_page_config(
    page_title="FASTA 质量检查器",
    page_icon="🧬",
    layout="wide",
)

st.title("FASTA 质量检查器")
st.write("上传 DNA 或蛋白质 FASTA 文件进行质量检查。")

sequence_type = st.sidebar.radio(
    "序列类型",
    [
        "DNA",
        "蛋白质",
    ],
)

display_mode = st.sidebar.radio(
    "显示结果",
    [
        "全部序列",
        "仅通过",
        "仅失败",
    ],
)

st.sidebar.header("质量阈值")

min_length = st.sidebar.number_input(
    "最短序列长度",
    min_value=0,
    value=0,
    step=1,
)

if sequence_type == "DNA":
    max_n_percent = st.sidebar.slider(
        "最大 N 比例（%）",
        min_value=0.0,
        max_value=100.0,
        value=100.0,
        step=1.0,
    )

    min_gc_percent = st.sidebar.slider(
        "最低 GC 比例（%）",
        min_value=0.0,
        max_value=100.0,
        value=0.0,
        step=1.0,
    )

    max_gc_percent = st.sidebar.slider(
        "最高 GC 比例（%）",
        min_value=0.0,
        max_value=100.0,
        value=100.0,
        step=1.0,
    )

    if min_gc_percent > max_gc_percent:
        st.error("最低 GC 比例不能大于最高 GC 比例。")
        st.stop()
else:
    st.sidebar.info(
        "蛋白质模式只检查序列长度和非法字符。"
    )

uploaded_file = st.file_uploader(
    "选择 FASTA 文件",
    type=["fasta", "fa", "fna"],
)

if uploaded_file is None:
    st.info("请先上传一个 FASTA 文件。")
    st.stop()

st.success(f"已选择文件：{uploaded_file.name}")

temp_path = None

try:
    suffix = Path(uploaded_file.name).suffix or ".fasta"

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix,
    ) as temp_file:
        temp_file.write(uploaded_file.getvalue())
        temp_path = temp_file.name

    if sequence_type == "DNA":
        results = analyze_fasta(
            temp_path,
            min_length=min_length,
            max_n_percent=max_n_percent,
            min_gc_percent=min_gc_percent,
            max_gc_percent=max_gc_percent,
        )

        result_data = [
            {
                "序列类型": "DNA",
                "序列 ID": result.sequence_id,
                "长度": result.length,
                "GC%": result.gc_percent,
                "N 数量": result.n_count,
                "N%": result.n_percent,
                "非法字符": result.invalid_chars,
                "失败原因": (
                    result.failure_reasons or "-"
                ),
                "是否通过": (
                    "PASS" if result.is_valid else "FAIL"
                ),
            }
            for result in results
        ]

    else:
        results = analyze_protein_fasta(
            temp_path,
            min_length=min_length,
        )

        result_data = [
            {
                "序列类型": "蛋白质",
                "序列 ID": result.sequence_id,
                "长度": result.length,
                "GC%": "-",
                "N 数量": "-",
                "N%": "-",
                "非法字符": result.invalid_chars,
                "失败原因": (
                    result.failure_reasons or "-"
                ),
                "是否通过": (
                    "PASS" if result.is_valid else "FAIL"
                ),
            }
            for result in results
        ]

except (FileNotFoundError, ValueError) as error:
    st.error(f"分析失败：{error}")

else:
    pass_count = sum(
        result.is_valid for result in results
    )
    fail_count = len(results) - pass_count

    col1, col2, col3 = st.columns(3)

    col1.metric("序列总数", len(results))
    col2.metric("通过数量", pass_count)
    col3.metric("失败数量", fail_count)

    if display_mode == "仅通过":
        display_data = [
            row
            for row, result in zip(
                result_data,
                results,
            )
            if result.is_valid
        ]
    elif display_mode == "仅失败":
        display_data = [
            row
            for row, result in zip(
                result_data,
                results,
            )
            if not result.is_valid
        ]
    else:
        display_data = result_data

    st.subheader("质量检查结果")

    if display_data:
        st.dataframe(display_data)
    else:
        st.info("当前筛选条件下没有序列。")

    st.subheader("下载结果")

    csv_buffer = StringIO()

    csv_writer = csv.DictWriter(
        csv_buffer,
        fieldnames=result_data[0].keys(),
    )
    csv_writer.writeheader()
    csv_writer.writerows(result_data)

    json_content = json.dumps(
        result_data,
        ensure_ascii=False,
        indent=2,
    )

    fasta_buffer = StringIO()

    with open(
        temp_path,
        "r",
        encoding="utf-8",
    ) as fasta_file:
        records = list(
            SeqIO.parse(
                fasta_file,
                "fasta",
            )
        )

    passing_records = (
        record
        for record, result in zip(
            records,
            results,
        )
        if result.is_valid
    )

    SeqIO.write(
        passing_records,
        fasta_buffer,
        "fasta",
    )

    download_col1, download_col2, download_col3 = (
        st.columns(3)
    )

    with download_col1:
        st.download_button(
            label="下载 CSV",
            data=csv_buffer.getvalue().encode(
                "utf-8-sig"
            ),
            file_name="fasta-qc-report.csv",
            mime="text/csv",
        )

    with download_col2:
        st.download_button(
            label="下载 JSON",
            data=json_content.encode("utf-8"),
            file_name="fasta-qc-report.json",
            mime="application/json",
        )

    with download_col3:
        st.download_button(
            label="下载通过序列 FASTA",
            data=fasta_buffer.getvalue().encode(
                "utf-8"
            ),
            file_name="passed-sequences.fasta",
            mime="text/plain",
        )

finally:
    if temp_path and os.path.exists(temp_path):
        os.unlink(temp_path)