#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="podagent"

# Create root
mkdir -p "${PROJECT_ROOT}"

# Data directories
mkdir -p "${PROJECT_ROOT}/data/raw"
mkdir -p "${PROJECT_ROOT}/data/interim"
mkdir -p "${PROJECT_ROOT}/data/processed"

# Source code
mkdir -p "${PROJECT_ROOT}/src/data_pipeline"
mkdir -p "${PROJECT_ROOT}/src/retriever"
mkdir -p "${PROJECT_ROOT}/src/models"
mkdir -p "${PROJECT_ROOT}/src/eval"
mkdir -p "${PROJECT_ROOT}/src/web/backend"
mkdir -p "${PROJECT_ROOT}/src/web/frontend"

# Configs
mkdir -p "${PROJECT_ROOT}/configs"

# Experiments (logs + checkpoints)
mkdir -p "${PROJECT_ROOT}/experiments/logs"
mkdir -p "${PROJECT_ROOT}/experiments/checkpoints"

# Notebooks
mkdir -p "${PROJECT_ROOT}/notebooks"

# Scripts
mkdir -p "${PROJECT_ROOT}/scripts"

# Touch a basic README
if [ ! -f "${PROJECT_ROOT}/README.md" ]; then
  cat > "${PROJECT_ROOT}/README.md" << 'EOF'
# PodAgent: Podcast Summarization

Directory layout:

- data/raw:        Original transcripts + metadata
- data/interim:    Chunked + diarized segments
- data/processed:  Final train/val/test datasets
- src/data_pipeline: Scraping, cleaning, diarization-aware chunking
- src/retriever:     Embedding index + retrieval
- src/models:        Fine-tuning (LoRA/QLoRA) + inference
- src/eval:          Automatic + human evaluation
- src/web/backend:   FastAPI service
- src/web/frontend:  Minimal UI
- configs:           Config files (paths, hyperparams, prompts)
- experiments/logs:  Logs, metrics
- experiments/checkpoints: Model checkpoints
- notebooks:         Exploration notebooks
- scripts:           Helper scripts
EOF
fi

echo "Project skeleton created under ./${PROJECT_ROOT}"
