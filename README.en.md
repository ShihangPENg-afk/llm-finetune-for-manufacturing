# llm-finetune-for-manufacturing

> Repository: https://github.com/ShihangPENg-afk/llm-finetune-for-manufacturing  
> 中文说明：[README.md](README.md)

Standalone **LoRA fine-tuning experiment repo** for validating the full pipeline from PDF technical manuals to Alpaca-format datasets, then to [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory) LoRA fine-tuning.

This repo does **not** aim to ship a production-ready model. It verifies the end-to-end workflow—data processing → dataset registration → LoRA training → weight export—on a local CPU setup, as a reproducible baseline before formal training on a GPU server.

---

## Related GitHub Repositories

| Repository | GitHub | Description |
|------------|--------|-------------|
| **llm-finetune-for-manufacturing** | https://github.com/ShihangPENg-afk/llm-finetune-for-manufacturing | This repo: PDF → LoRA fine-tuning experiment |
| **rag-agentic-system** | https://github.com/ShihangPENg-afk/rag-agentic-system | Agentic RAG main app (LoRA **not integrated yet**) |
| **predictive-maintenance-mini** | https://github.com/ShihangPENg-afk/predictive-maintenance-mini | Industrial ML inference API (no code dependency on this repo) |

---

## Relationship with rag-agentic-system

| Project | GitHub | Role | Status |
|---------|--------|------|--------|
| **rag-agentic-system** | https://github.com/ShihangPENg-afk/rag-agentic-system | Agentic RAG Q&A: PDF upload, FAISS retrieval, LangGraph agent, RAGAS eval | Main application repo (engineering POC) |
| **llm-finetune-for-manufacturing** | https://github.com/ShihangPENg-afk/llm-finetune-for-manufacturing | PDF → Alpaca dataset → Qwen2-7B LoRA fine-tuning | This repo |

**How they relate:**

- Both sit on the same PDF knowledge pipeline at different stages, but **code, dependencies, and deployment are fully independent**, each with its own virtual environment.
- **The LoRA fine-tuned model is not integrated into rag-agentic-system yet.** rag-agentic-system’s generation node and RAGAS evaluation still call the DashScope online API (`qwen-plus`); they do not load adapter weights from this repo’s `outputs/`.
- rag-agentic-system RAGAS metrics (faithfulness, answer_relevancy, etc.) **only reflect online API Q&A performance** and are not directly comparable to training loss or before/after results in this repo.

---

## Data Processing Pipeline

```
Corpus (data/demo_corpus/*.txt)
    │
    ▼  scripts/generate_demo_pdfs.py   (or place your own PDFs under data/raw_pdfs/)
PDF (data/raw_pdfs/)
    │
    ▼  scripts/extract_chunks.py
chunks.json (text chunks)
    │
    ▼  scripts/build_alpaca_dataset.py
alpaca_train.json + dataset_info.json
    │
    ▼
LLaMA-Factory dataset registration (manual_alpaca)
```

| Step | Script | Input | Output | Notes |
|------|--------|-------|--------|-------|
| Demo PDFs | `scripts/generate_demo_pdfs.py` | `data/demo_corpus/manual*.txt` | `data/raw_pdfs/manual*.pdf` | Optional if you provide your own PDFs |
| PDF chunking | `scripts/extract_chunks.py` | `data/raw_pdfs/*.pdf` | `data/processed/chunks.json` | PyMuPDF text extraction; ~800-char chunks |
| Build Alpaca data | `scripts/build_alpaca_dataset.py` | `chunks.json` | `alpaca_train.json`, `dataset_info.json` | Noise cleanup, dedup, length filter; 4 instruction templates rotated |

---

## Dataset Info

| Attribute | Value |
|-----------|-------|
| Sample count | **133** (demo corpus pipeline: `generate_demo_pdfs.py` → 5 PDFs) |
| Instruction templates | **4** (rotated to avoid single-instruction overfitting) |
| Format | Alpaca (`instruction` / `input` / `output`) |
| Dataset name | `manual_alpaca` |

`dataset_info.json` maps Alpaca fields via `prompt` / `query` / `response`:

```json
{
  "manual_alpaca": {
    "file_name": "alpaca_train.json",
    "formatting": "alpaca",
    "columns": {
      "prompt": "instruction",
      "query": "input",
      "response": "output"
    }
  }
}
```

Instruction template examples:

- Summarize the core information in the given material.
- Read the material below and extract key information.
- Summarize the main points of the following content.
- Explain what this material is mainly about.

*(Templates in the repo are in Chinese, matching the source PDF language.)*

---

## Training Configuration

| Item | Value |
|------|-------|
| Base model | `Qwen/Qwen2-7B-Instruct` |
| Framework | [LLaMA-Factory](https://github.com/hiyouga/LLaMA-Factory) (tested with `>=0.9.3`) |
| Method | LoRA (`rank: 4`, `alpha: 8`) |
| Environment | Intel MacBook Pro CPU (x86_64, 16GB RAM, no GPU/MPS) |
| Dataset | `manual_alpaca` |
| `max_samples` | **50** (sampled from 132 rows to reduce CPU training time) |
| `num_train_epochs` | **1** |
| Precision | float32 (`bf16` / `fp16` disabled for CPU stability) |
| Config file | `configs/qwen2_7b_lora_cpu.yaml` |
| Output | `outputs/qwen2_7b_lora_cpu/` (ignored by `.gitignore`) |

**Scope:** Local CPU is for **workflow verification only**, not model quality. 50 samples and 1 epoch are enough to confirm the pipeline and training script; formal training should run on a GPU server.

> **After clone:** `data/processed/*.json` and `data/raw_pdfs/*.pdf` are not committed. First run `scripts/generate_demo_pdfs.py` to build 5 demo PDFs from `data/demo_corpus/`, then run `extract_chunks.py` and `build_alpaca_dataset.py` to generate `chunks.json`, `alpaca_train.json`, and `dataset_info.json` (written automatically by `build_alpaca_dataset.py`). You may also use your own PDFs under `data/raw_pdfs/`. The **133**-sample count comes from the reproducible demo pipeline (the 2026-06-09 original PDF run yielded 132; layout differences may differ by 1).

---

## Run Commands

Clone this repository:

```bash
git clone https://github.com/ShihangPENg-afk/llm-finetune-for-manufacturing.git
cd llm-finetune-for-manufacturing
```

From the project root:

```bash
# 0. Install dependencies
pip install -r requirements.txt

# 1. Generate demo PDFs (or skip and provide your own under data/raw_pdfs/)
python scripts/generate_demo_pdfs.py

# 2. PDF chunking
python scripts/extract_chunks.py data/raw_pdfs/

# 3. Build Alpaca dataset (also writes dataset_info.json)
python scripts/build_alpaca_dataset.py

# 4. Sample quality check
python scripts/sample_check.py

# 5. Start CPU LoRA training (downloads Qwen2-7B-Instruct from Hugging Face; large & slow)
bash scripts/train_qwen2_7b_lora_cpu.sh

# 6. Before/after eval (optional; 7B CPU inference is not practical locally)
python scripts/eval_before_after_cpu.py --phase before
python scripts/eval_before_after_cpu.py --phase after
```

After a successful run:

| Artifact | Path |
|----------|------|
| Text chunks | `data/processed/chunks.json` |
| Alpaca training data | `data/processed/alpaca_train.json` |
| LLaMA-Factory dataset config | `data/processed/dataset_info.json` |
| LoRA weights | `outputs/qwen2_7b_lora_cpu/adapter_model.safetensors` (local only, not in Git) |

---

## Current Limitations

- **Local hardware:** Experiments ran on Intel MacBook Pro CPU (16GB, no GPU). First base-model download ~1h+; 50 training steps ~4h; full 7B CPU inference often OOMs or takes 30–60+ min per question—**not suitable** for full local training or eval.
- **Workflow-only scope:** `max_samples: 50` and 1 epoch verify the pipeline only; **not sufficient for a usable domain model**.
- **LoRA not in rag-agentic-system:** Weights live under this repo’s `outputs/`; rag-agentic-system still uses DashScope online API—**not connected yet**.
- **No production auth or cloud deploy:** Training and weights are local experiment artifacts.

---

## Documentation

| Document | Description |
|----------|-------------|
| [docs/experiment_record.md](docs/experiment_record.md) | Experiment log (hardware, loss, adapter output) |
| [docs/delivery_checklist.md](docs/delivery_checklist.md) | Acceptance checklist for the CPU workflow |

---

## Roadmap

- Move data pipeline and training config to a GPU server; train on all 132 samples with more epochs
- Run before/after evaluation on GPU
- Evaluate integrating the LoRA adapter into rag-agentic-system’s generation node (**not integrated yet**)

---

## Directory Layout

```
data/
  demo_corpus/           # Demo text sources (manual1.txt–manual5.txt, committed)
  raw_pdfs/              # Source PDFs (*.pdf gitignored; generated or placed locally)
  processed/
    chunks.json          # Text chunks (generated locally, gitignored)
    alpaca_train.json    # Alpaca data (generated locally, gitignored)
    dataset_info.json    # LLaMA-Factory config (generated by build_alpaca_dataset.py)
configs/
  qwen2_7b_lora_cpu.yaml # CPU LoRA training config
scripts/
  generate_demo_pdfs.py  # Build demo PDFs from demo_corpus
  extract_chunks.py
  build_alpaca_dataset.py
  sample_check.py
  train_qwen2_7b_lora_cpu.sh
  eval_before_after_cpu.py
outputs/                 # Training output (gitignored; local only)
docs/
  experiment_record.md
  delivery_checklist.md
LICENSE
requirements.txt
README.md                # Chinese
README.en.md             # English (this file)
```
