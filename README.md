# FASTA QC

用于检查 DNA FASTA 文件基本质量指标的 Python 命令行工具。

## 功能

- 读取多序列 FASTA 文件
- 计算序列长度和 GC 含量
- 统计 N 数量和 N 比例
- 支持标准 IUPAC DNA 模糊碱基
- 检查 IUPAC 规则之外的非法字符
- 检查重复的 FASTA 序列 ID
- 设置最短序列长度
- 设置最大 N 比例
- 设置最低和最高 GC 比例
- 显示失败原因
- 导出 CSV 报告
- 导出 JSON 报告
- 导出通过检查的 FASTA 文件
- 自动测试

## 安装

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## 基础运行

```powershell
python -m app.cli data\example.fasta
```

## 使用质量阈值

```markdown
要求序列长度至少为 7，N 比例不超过 20%，GC 比例在 40% 到 60% 之间：

```powershell
python -m app.cli data\example.fasta `
  --min-length 7 `
  --max-n-percent 20 `
  --min-gc 40 `
  --max-gc 60
  --json-output results/report.json
```

## 导出 CSV

```markdown
```powershell
python -m app.cli data\example.fasta `
  --min-length 7 `
  --max-n-percent 20 `
  --min-gc 40 `
  --max-gc 60 `
  -o results\report-v03.csv

## 参数

| 参数 | 说明 | 默认值 |
|---|---|---|
| `input` | 输入 FASTA 文件 | 必填 |
| `--min-length` | 最短序列长度 | 0 |
| `--max-n-percent` | 最大 N 比例 | 100 |
| `--min-gc` | 最低 GC 比例 | 0 |
| `--max-gc` | 最高 GC 比例 | 100 |
| `--json-output` | JSON 输出路径 | 不输出 |
| `--filtered-output` | 通过检查的 FASTA 输出路径 | 不输出 |
| `-o, --output` | CSV 输出路径 | 不输出 |


## 导出通过检查的 FASTA

```powershell
python -m app.cli data/example.fasta `
  --min-length 7 `
  --max-n-percent 20 `
  --filtered-output results/passed.fasta


## 测试并提交

```powershell
python -m pytest -q
```

## 当前规则

允许的 DNA 字符：

```text
A C G T R Y S W K M B D H V N
```
R、Y、S、W、K、M、B、D、H、V 和 N 是合法的 IUPAC 模糊碱基。
GC 比例目前只统计明确的 G 和 C；模糊碱基不计入 GC 数量。
例如 X、Z、数字和特殊符号仍会被判定为非法字符。

以下情况会判定为失败：

- 序列为空
- 包含非法字符
- 长度小于 `--min-length`
- N 比例超过 `--max-n-percent`
- GC 比例低于 `--min-gc`
- GC 比例超过 `--max-gc`
- 序列 ID 重复

## 使用范围

本工具用于教学、科研和非临床 FASTA 数据质量检查。

分析结果需要由研究人员复核。本工具未经临床验证，不能单独用于疾病诊断、治疗决策或正式临床报告。