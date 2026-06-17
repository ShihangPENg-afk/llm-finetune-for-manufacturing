# llm-finetune-for-manufacturing 验收清单

> 最后核对：2026-06-17  
> 关联文档：[README.md](../README.md) · [README.en.md](../README.en.md) · [experiment_record.md](experiment_record.md)  
> 关联主项目：[rag-agentic-system](https://github.com/ShihangPENg-afk/rag-agentic-system)（LoRA 尚未接入）

---

## 如何使用本清单

| 视角 | 含义 | 适用章节 |
|------|------|----------|
| **公开仓库（clone 即可核对）** | 脚本、配置、演示语料已提交 Git；PDF / 训练产物需本地生成 | 第 A 节 |
| **维护者本地验收（2026-06-09）** | 在 Intel Mac CPU 上已跑通的历史结果；`outputs/` 与原始 PDF 不提交 Git | 第 B 节 |

公开访客 clone 后，按 [README.md](../README.md) 运行 `generate_demo_pdfs.py` → `extract_chunks.py` → `build_alpaca_dataset.py`，应得到 **133** 条 Alpaca 样本（2026-06-09 原始 PDF 实验为 **132** 条，版式差异可能导致 ±1）。

---

## 验收状态总览

| 类别 | 公开仓库 | 维护者本地（2026-06-09） |
|------|----------|--------------------------|
| 脚本与配置 | ✅ 已提交 | ✅ |
| 演示语料 `data/demo_corpus/` | ✅ 已提交 | ✅ |
| 数据处理（PDF → Alpaca） | ✅ 可复现 | ✅ 132 条（原始 PDF） |
| LLaMA-Factory 配置与训练 | ✅ 可执行 | ✅ 已跑通 |
| 文档与实验记录 | ✅ | ✅ |
| 效果评测与 rag-agentic-system 接入 | — | ❌ 未完成（见 B-7） |

---

## A. 公开 clone 可复现项

### A-1. 演示语料与 PDF 生成脚本

- [x] `data/demo_corpus/manual1.txt` ~ `manual5.txt` 已提交 Git
- [x] `scripts/generate_demo_pdfs.py` 可从语料生成 5 份 PDF 到 `data/raw_pdfs/`

**验收命令：**

```bash
python scripts/generate_demo_pdfs.py
ls data/raw_pdfs/manual*.pdf | wc -l
# 预期输出：5
```

### A-2. 数据处理脚本

- [x] `scripts/extract_chunks.py` 可正常执行
- [x] `scripts/build_alpaca_dataset.py` 可正常执行，并**自动写入** `dataset_info.json`
- [x] `scripts/sample_check.py` 可正常执行

**验收命令：**

```bash
python scripts/extract_chunks.py data/raw_pdfs/
python scripts/build_alpaca_dataset.py
python scripts/sample_check.py
python -c "import json; print(len(json.load(open('data/processed/chunks.json'))))"
# 预期输出：133
python -c "import json; print(len(json.load(open('data/processed/alpaca_train.json'))))"
# 预期输出：133
python -c "import json; print('manual_alpaca' in json.load(open('data/processed/dataset_info.json')))"
# 预期输出：True
```

### A-3. LLaMA-Factory 训练配置

- [x] 配置文件：`configs/qwen2_7b_lora_cpu.yaml`
- [x] 基座模型：`Qwen/Qwen2-7B-Instruct`
- [x] 微调方式：`finetuning_type: lora`
- [x] 运行环境：CPU（`bf16: false`, `fp16: false`）
- [x] 启动脚本：`scripts/train_qwen2_7b_lora_cpu.sh`

### A-4. README 边界说明

- [x] 说明 CPU 环境限制与 workflow 验证定位
- [x] 说明 LoRA 模型尚未接入 rag-agentic-system
- [x] 说明 clone 后需运行 `generate_demo_pdfs.py` 或自备 PDF
- [x] 说明 `dataset_info.json` 由 `build_alpaca_dataset.py` 生成

---

## B. 维护者本地验收（2026-06-09，产物不提交 Git）

> 以下勾选项描述维护者在原始 PDF 与 Intel Mac CPU 上的历史跑通结果，**不代表** clone 后仓库内已自带这些文件。

### B-1. PDF 切块

- [x] `data/raw_pdfs/` 下共 **5** 份 PDF（`manual1.pdf` ~ `manual5.pdf`）
- [x] 输出 `data/processed/chunks.json`，共 **132** 个 chunk

### B-2. Alpaca 数据集

- [x] 输出 `data/processed/alpaca_train.json`，共 **132** 条样本
- [x] 每条样本包含 `instruction` / `input` / `output` 三元组
- [x] **4** 种 instruction 模板轮换分配（各 33 条）

**备注：** `output 为 input 前缀的样本数: 4` 为摘要构造策略所致，属预期现象。

### B-3. dataset_info.json

- [x] 数据集名称：`manual_alpaca`
- [x] `columns` 映射：`prompt`→instruction，`query`→input，`response`→output
- [x] 与 `configs/qwen2_7b_lora_cpu.yaml` 中 `dataset_dir` / `dataset` 一致

### B-4. CPU LoRA 训练

- [x] `max_samples: 50`，`num_train_epochs: 1`（流程验证，非正式训练）
- [x] 训练 50 step 总耗时约 **4h14m**

### B-5. 训练输出（本地 `outputs/`，已被 `.gitignore` 忽略）

- [x] 输出目录：`outputs/qwen2_7b_lora_cpu/`
- [x] LoRA 权重：`adapter_model.safetensors`（约 40 MB）
- [x] loss 日志：`trainer_log.jsonl`；曲线：`training_loss.png`
- [x] 平均 train_loss ≈ **0.42**；step 50 loss ≈ **0.158**

**训练结果摘要：**

| 指标 | 值 |
|------|-----|
| 是否成功启动 | 是 |
| 训练 step 数 | 50 |
| 训练耗时 | 约 4h14m |
| 最终 loss | 0.158（step 50） |
| adapter 文件 | 已生成 |

### B-6. 可选评测脚本

- [x] `scripts/eval_before_after_cpu.py` 已就绪（本地 CPU 7B 推理不具可行性，未作为验收项）

### B-7. 未完成项（backlog）

| 项目 | 状态 | 说明 |
|------|------|------|
| before/after 效果对比 | 未完成 | 16GB CPU 下 7B 推理易 OOM |
| 全量样本正式训练 | 未完成 | 当前仅 50/132 条、1 epoch |
| GPU 环境迁移 | 未完成 | 需全量数据与更多 epoch |
| LoRA 接入 rag-agentic-system | 未完成 | 主项目仍使用 DashScope 在线 API |
| 训练输出提交 Git | 不适用 | `outputs/` 已被 `.gitignore` 忽略 |
| 验证集与 eval 指标 | 未完成 | 无 `eval_loss` / `eval_accuracy` |

---

## 验收结论

- **公开仓库：** 满足 **A-1 ~ A-4** 后，clone 用户可独立复现「演示 PDF → Alpaca → `dataset_info.json`」数据管线。
- **维护者本地：** **B-1 ~ B-5** 记录 2026-06-09 CPU 训练已跑通；**B-7** 为后续迭代 backlog，不影响「PDF → Alpaca → LoRA 训练 → 权重保存」链路曾验证成功的结论。
