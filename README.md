# FASTA QC

用于检查 DNA FASTA 文件基本质量指标的 Python 命令行工具。

## 功能

- 读取多序列 FASTA 文件
- 计算序列长度和 GC 含量
- 统计 N 数量和 N 比例
- 检查非法字符
- 设置最短序列长度
- 设置最大 N 比例
- 设置最低和最高 GC 比例
- 显示失败原因
- 导出 CSV 报告
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
| `-o, --output` | CSV 输出路径 | 不输出 |

## 测试

```powershell
python -m pytest -q
```

## 当前规则

允许的 DNA 字符：

```text
A C G T N
```

以下情况会判定为失败：

- 序列为空
- 包含非法字符
- 长度小于 `--min-length`
- N 比例超过 `--max-n-percent`
- GC 比例低于 `--min-gc`
- GC 比例超过 `--max-gc`

## 使用范围

本工具用于教学、科研和非临床 FASTA 数据质量检查。

分析结果需要由研究人员复核。本工具未经临床验证，不能单独用于疾病诊断、治疗决策或正式临床报告。