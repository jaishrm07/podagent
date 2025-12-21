from pathlib import Path

# Resolve repository root (two levels up from this file: src/podagent/config.py -> src -> repo)
BASE_DIR = Path(__file__).resolve().parents[2]

# Data paths
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
TRANSCRIPTS_DIR = RAW_DIR / "transcripts"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"

# Experiment paths
EXPERIMENTS_DIR = BASE_DIR / "experiments"
LOGS_DIR = EXPERIMENTS_DIR / "logs"
CHECKPOINTS_DIR = EXPERIMENTS_DIR / "checkpoints"

# Config path
CONFIGS_DIR = BASE_DIR / "configs"


def ensure_directories() -> None:
    """
    Create expected directories if they do not already exist.
    """
    for path in [
        DATA_DIR,
        RAW_DIR,
        TRANSCRIPTS_DIR,
        INTERIM_DIR,
        PROCESSED_DIR,
        LOGS_DIR,
        CHECKPOINTS_DIR,
    ]:
        path.mkdir(parents=True, exist_ok=True)
