from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import TESTING_FILE, TRAINING_FILE


def load_dataset(csv_path: Path) -> pd.DataFrame:
    """Load a UNSW-NB15 CSV file into a pandas DataFrame."""
    return pd.read_csv(csv_path)


def load_training_data() -> pd.DataFrame:
    return load_dataset(TRAINING_FILE)


def load_testing_data() -> pd.DataFrame:
    return load_dataset(TESTING_FILE)


def summarize_dataframe(df: pd.DataFrame) -> dict:
    """Create a compact profile that is useful for first-pass exploration."""
    label_counts = df["label"].value_counts(dropna=False).to_dict() if "label" in df.columns else {}
    attack_counts = df["attack_cat"].value_counts(dropna=False).to_dict() if "attack_cat" in df.columns else {}

    return {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "missing_values_per_column": df.isna().sum().sort_values(ascending=False).to_dict(),
        "duplicate_rows": int(df.duplicated().sum()),
        "label_distribution": label_counts,
        "attack_category_distribution": attack_counts,
    }
