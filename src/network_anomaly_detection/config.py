from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw" / "archive"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

TRAINING_FILE = RAW_DATA_DIR / "UNSW_NB15_training-set.csv"
TESTING_FILE = RAW_DATA_DIR / "UNSW_NB15_testing-set.csv"
