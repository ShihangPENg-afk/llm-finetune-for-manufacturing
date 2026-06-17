# llm-finetune-for-manufacturing

> **Repository:** https://github.com/ShihangPENg-afk/llm-finetune-for-manufacturing  
> 中文说明：[README.md](README.md)

A standalone experiment repository that validates a **LoRA fine-tuning workflow** for manufacturing technical manuals. The goal is to build hands-on training experience and confirm that the end-to-end pipeline runs correctly — **not** to ship a production-ready model.

---

## 1. Project Overview

This project walks through the full path from PDF manuals to a LoRA adapter on **Qwen2-7B-Instruct**, using [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory) as the training framework.

| Aspect | Description |
|--------|-------------|
| **Domain** | Manufacturing technical manuals (demo corpus included) |
| **Method** | LoRA fine-tuning on `Qwen/Qwen2-7B-Instruct` |
| **Purpose** | Workflow validation and training experience |
| **Not in scope** | Production deployment, domain-grade model quality, or cloud serving |

The repository is intentionally scoped as a **reproducible baseline** before any full GPU training on a dedicated server.

---

## 2. Pipeline

```
PDF manuals
    │
    ▼  scripts/extract_chunks.py
text chunks (chunks.json)
    │
    ▼  scripts/build_alpaca_dataset.py
Alpaca dataset (alpaca_train.json)
    │
    ▼  dataset registration
dataset_info.json  →  manual_alpaca
    │
    ▼  LLaMA-Factory
Qwen2-7B-Instruct + LoRA training
    │
    ▼
LoRA adapter (adapter weights + config)
```

| Stage | Artifact / Tool | Role |
|-------|-----------------|------|
| Source | PDF manuals (`data/raw_pdfs/`) | Raw technical manual content |
| Chunking | `chunks.json` | Text segments (~800 chars) extracted via PyMuPDF |
| Dataset | `alpaca_train.json` | Alpaca triplets: `instruction` / `input` / `output` |
| Registration | `dataset_info.json` | Maps fields for LLaMA-Factory (`manual_alpaca`) |
| Training | [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory) | LoRA fine-tuning orchestration |
| Base model | `Qwen/Qwen2-7B-Instruct` | Instruction-tuned 7B backbone |
| Output | LoRA adapter | Low-rank weight deltas saved under `outputs/` |

Demo PDFs can be generated from `data/demo_corpus/` via `scripts/generate_demo_pdfs.py`, or you can supply your own PDFs.

---

## 3. Dataset Summary

| Metric | Value |
|--------|-------|
| Alpaca samples | **132** |
| Instruction templates | **4** (rotated to avoid single-template overfitting) |
| Dataset name | `manual_alpaca` |
| Format | Alpaca (`instruction`, `input`, `output`) |

**CPU subset training** (local workflow verification):

| Setting | Value |
|---------|-------|
| `max_samples` | **50** (sampled from the full set) |
| `num_train_epochs` | **1** |

This subset is enough to confirm that data processing, dataset registration, and training scripts work end-to-end — not to produce a usable domain model.

---

## 4. Hardware Limitation

All experiments in this repository were run under **severe hardware constraints**:

| Constraint | Detail |
|------------|--------|
| Machine | Intel MacBook Pro (x86_64, 16 GB RAM) |
| Accelerator | **No NVIDIA GPU** (no Apple MPS either) |
| Training mode | Pure CPU, float32 |
| Full GPU training | **Deferred** — planned for a dedicated GPU server |

CPU training is slow (base-model download and 50-step runs take hours) and is unsuitable for full-dataset training or 7B inference at scale.

---

## 5. Outputs

After a successful run, local artifacts include:

| Output | Location / description |
|--------|------------------------|
| Adapter config | `outputs/qwen2_7b_lora_cpu/` — LoRA hyperparameters and adapter metadata |
| Training loss | Trainer logs and loss curves under `outputs/` |
| Logs | LLaMA-Factory / training run logs (local only) |
| Experiment record | [docs/experiment_record.md](docs/experiment_record.md) — hardware, loss summary, adapter details |

Generated data and weights (`data/processed/*.json`, `outputs/`) are **not committed** to Git; clone the repo and run the pipeline locally to reproduce them.

---

## 6. Relationship with rag-agentic-system

This repo and [rag-agentic-system](https://github.com/ShihangPENg-afk/rag-agentic-system) sit on the same PDF knowledge theme but are **fully independent** (separate code, dependencies, and deployment).

| Topic | Status |
|-------|--------|
| LoRA adapter integration | **Not integrated** — rag-agentic-system does not load weights from this repo’s `outputs/` |
| Generation in rag-agentic-system | Still uses DashScope online API (`qwen-plus`) |
| RAGAS evaluation in rag-agentic-system | Evaluates the **RAG system only** (retrieval + online generation); metrics are **not** tied to this repo’s training loss or before/after fine-tuning results |

Connecting the LoRA adapter to the rag-agentic-system generation node remains a future evaluation step.

---

## 7. Known Limitations

- **Not production-grade** — workflow validation only; 50 samples × 1 epoch is insufficient for domain adaptation.
- **No full GPU training** — full 132-sample, multi-epoch training has not been run in this repo.
- **Limited before/after evaluation** — 7B CPU inference is impractical locally; systematic pre/post fine-tuning comparison is deferred to a GPU environment.
- **No cloud deploy or production auth** — all artifacts are local experiment outputs.

---

## Quick Start

```bash
git clone https://github.com/ShihangPENg-afk/llm-finetune-for-manufacturing.git
cd llm-finetune-for-manufacturing
pip install -r requirements.txt

python scripts/generate_demo_pdfs.py          # optional demo PDFs
python scripts/extract_chunks.py data/raw_pdfs/
python scripts/build_alpaca_dataset.py
bash scripts/train_qwen2_7b_lora_cpu.sh
```

See [docs/experiment_record.md](docs/experiment_record.md) and [docs/delivery_checklist.md](docs/delivery_checklist.md) for detailed experiment notes and acceptance criteria.

---

## Related Repositories

| Repository | Role |
|------------|------|
| [rag-agentic-system](https://github.com/ShihangPENg-afk/rag-agentic-system) | Agentic RAG Q&A (FAISS, LangGraph, RAGAS) |
| [predictive-maintenance-mini](https://github.com/ShihangPENg-afk/predictive-maintenance-mini) | Industrial ML inference API (no code dependency) |
