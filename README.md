# FASTA QC

用于检查 DNA FASTA 文件基本质量指标的 Python 命令行工具。

## 功能

- 读取多序列 FASTA 文件
- 计算序列长度
- 计算 GC 含量
- 统计 N 碱基数量
- 检查非法字符
- 导出 CSV 报告
- 自动测试

## 安装

创建并激活虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

## 使用范围

本工具用于教学、科研和非临床 FASTA 数据质量检查。

分析结果需要由研究人员复核。本工具未经临床验证，
不能单独用于疾病诊断、治疗决策或正式临床报告。