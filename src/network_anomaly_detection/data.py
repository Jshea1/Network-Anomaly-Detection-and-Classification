from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .config import PROCESSED_DATA_DIR, TESTING_FILE, TRAINING_FILE


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


def build_feature_matrix(
    df: pd.DataFrame,
    target_column: str,
    columns_to_drop: list[str] | None = None,
) -> tuple[pd.DataFrame, pd.Series]:
    """Split a dataframe into features and a target vector."""
    drop_columns = set(columns_to_drop or [])
    drop_columns.add(target_column)

    features = df.drop(columns=[column for column in drop_columns if column in df.columns]).copy()
    target = df[target_column].copy()
    return features, target


def save_json(data: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def save_dataframe(df: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)


def save_processed_splits(
    x_train: pd.DataFrame,
    x_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
    prefix: str,
) -> None:
    """Persist processed train/test splits for transparency and reuse."""
    save_dataframe(x_train, PROCESSED_DATA_DIR / f"{prefix}_x_train.csv")
    save_dataframe(x_test, PROCESSED_DATA_DIR / f"{prefix}_x_test.csv")
    save_dataframe(y_train.to_frame(name=prefix), PROCESSED_DATA_DIR / f"{prefix}_y_train.csv")
    save_dataframe(y_test.to_frame(name=prefix), PROCESSED_DATA_DIR / f"{prefix}_y_test.csv")
