from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier

from network_anomaly_detection.config import PROCESSED_DATA_DIR, PROJECT_ROOT
from network_anomaly_detection.data import (
    build_feature_matrix,
    load_testing_data,
    load_training_data,
    save_json,
    save_processed_splits,
)


REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"


def build_preprocessor(x_train: pd.DataFrame) -> ColumnTransformer:
    categorical_columns = x_train.select_dtypes(include=["object"]).columns.tolist()
    numeric_columns = [column for column in x_train.columns if column not in categorical_columns]

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, numeric_columns),
            ("categorical", categorical_pipeline, categorical_columns),
        ]
    )


def build_model(x_train: pd.DataFrame, multiclass: bool) -> Pipeline:
    criterion = "gini"
    max_depth = 12 if multiclass else 10
    min_samples_leaf = 4 if multiclass else 3

    return Pipeline(
        steps=[
            ("preprocessor", build_preprocessor(x_train)),
            (
                "classifier",
                DecisionTreeClassifier(
                    random_state=42,
                    class_weight="balanced",
                    criterion=criterion,
                    max_depth=max_depth,
                    min_samples_leaf=min_samples_leaf,
                ),
            ),
        ]
    )


def compute_metrics(y_true: pd.Series, y_pred: pd.Series) -> dict:
    precision, recall, f1_score, _ = precision_recall_fscore_support(
        y_true,
        y_pred,
        average="weighted",
        zero_division=0,
    )

    return {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "precision_weighted": round(float(precision), 4),
        "recall_weighted": round(float(recall), 4),
        "f1_weighted": round(float(f1_score), 4),
    }


def save_confusion_matrix(
    y_true: pd.Series,
    y_pred: pd.Series,
    labels: list,
    title: str,
    output_path: Path,
) -> None:
    matrix = confusion_matrix(y_true, y_pred, labels=labels)

    plt.figure(figsize=(10, 7))
    plt.imshow(matrix, interpolation="nearest", cmap="Blues")
    plt.title(title)
    plt.colorbar()
    tick_positions = range(len(labels))
    plt.xticks(tick_positions, labels, rotation=45, ha="right")
    plt.yticks(tick_positions, labels)
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")

    for row_index in range(matrix.shape[0]):
        for column_index in range(matrix.shape[1]):
            plt.text(
                column_index,
                row_index,
                str(matrix[row_index, column_index]),
                ha="center",
                va="center",
                color="black",
            )

    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close()


def save_classification_report(
    y_true: pd.Series,
    y_pred: pd.Series,
    output_path: Path,
) -> None:
    report = classification_report(y_true, y_pred, zero_division=0)
    output_path.write_text(report, encoding="utf-8")


def format_binary_label(label: int) -> str:
    return "Attack" if int(label) == 1 else "Normal"


def explain_decision_path(model: Pipeline, sample: pd.DataFrame, max_rules: int = 4) -> list[str]:
    preprocessor = model.named_steps["preprocessor"]
    classifier = model.named_steps["classifier"]

    transformed = preprocessor.transform(sample)
    transformed_dense = transformed.toarray()[0] if hasattr(transformed, "toarray") else np.asarray(transformed)[0]
    feature_names = preprocessor.get_feature_names_out()

    node_indicator = classifier.decision_path(transformed)
    leaf_id = classifier.apply(transformed)[0]
    node_index = node_indicator.indices[node_indicator.indptr[0] : node_indicator.indptr[1]]

    rules: list[str] = []
    for node_id in node_index:
        if node_id == leaf_id:
            continue

        feature_index = classifier.tree_.feature[node_id]
        threshold = classifier.tree_.threshold[node_id]
        feature_name = feature_names[feature_index]
        actual_value = transformed_dense[feature_index]
        comparator = "<=" if actual_value <= threshold else ">"
        rules.append(f"`{feature_name}` {comparator} `{threshold:.4f}` (actual `{actual_value:.4f}`)")

        if len(rules) >= max_rules:
            break

    return rules


def write_binary_prediction_examples(
    model: Pipeline,
    x_test: pd.DataFrame,
    y_test: pd.Series,
    output_path: Path,
) -> None:
    predictions = pd.Series(model.predict(x_test), index=x_test.index)
    probabilities = model.predict_proba(x_test)

    example_indices: list[int] = []
    for class_value in [0, 1]:
        class_matches = y_test[(y_test == class_value) & (predictions == class_value)].index.tolist()[:3]
        example_indices.extend(class_matches)

    lines = [
        "# Binary Prediction Examples",
        "",
        "These examples show how the binary anomaly detection model labeled test-set traffic as either `Normal` or `Attack`.",
        "The evidence section lists a few Decision Tree rules that were active for that prediction.",
        "",
    ]

    for index in example_indices:
        sample = x_test.loc[[index]]
        actual_label = int(y_test.loc[index])
        predicted_label = int(predictions.loc[index])
        confidence = float(probabilities[x_test.index.get_loc(index)][predicted_label])
        evidence_rules = explain_decision_path(model, sample)

        lines.append(f"## Sample {index}")
        lines.append("")
        lines.append(f"- Actual label: `{format_binary_label(actual_label)}`")
        lines.append(f"- Predicted label: `{format_binary_label(predicted_label)}`")
        lines.append(f"- Model confidence: `{confidence:.4f}`")
        lines.append("- Evidence:")
        for rule in evidence_rules:
            lines.append(f"  - {rule}")
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def train_and_evaluate(
    task_name: str,
    x_train: pd.DataFrame,
    y_train: pd.Series,
    x_test: pd.DataFrame,
    y_test: pd.Series,
    multiclass: bool,
) -> dict:
    model = build_model(x_train, multiclass=multiclass)
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)

    labels = sorted(pd.Series(y_test).dropna().unique().tolist())
    metrics = compute_metrics(y_test, predictions)

    save_confusion_matrix(
        y_test,
        predictions,
        labels=labels,
        title=f"{task_name.replace('_', ' ').title()} Confusion Matrix",
        output_path=FIGURES_DIR / f"{task_name}_confusion_matrix.png",
    )
    save_classification_report(
        y_test,
        predictions,
        REPORTS_DIR / f"{task_name}_classification_report.txt",
    )

    if not multiclass:
        write_binary_prediction_examples(
            model,
            x_test,
            y_test,
            REPORTS_DIR / "binary_prediction_examples.md",
        )

    return {
        "task": task_name,
        "metrics": metrics,
        "class_labels": labels,
    }


def write_project_report(results: dict) -> None:
    binary_metrics = results["binary_detection"]["metrics"]
    multiclass_metrics = results["attack_classification"]["metrics"]

    report_text = f"""# Final Project Summary

## Project Goal

This project uses the UNSW-NB15 dataset to detect whether network traffic is normal or malicious and to classify the attack category when present.

## Approach

- Used the official training and testing CSV files included with the dataset.
- Removed identifier and target-leakage columns where appropriate.
- Applied median imputation to numeric features and most-frequent imputation plus one-hot encoding to categorical features.
- Trained Decision Tree classifiers for:
  - Binary anomaly detection using `label`
  - Multi-class traffic classification using `attack_cat`

## Results

### Binary Anomaly Detection

- Accuracy: {binary_metrics["accuracy"]}
- Precision (weighted): {binary_metrics["precision_weighted"]}
- Recall (weighted): {binary_metrics["recall_weighted"]}
- F1-score (weighted): {binary_metrics["f1_weighted"]}

### Attack Category Classification

- Accuracy: {multiclass_metrics["accuracy"]}
- Precision (weighted): {multiclass_metrics["precision_weighted"]}
- Recall (weighted): {multiclass_metrics["recall_weighted"]}
- F1-score (weighted): {multiclass_metrics["f1_weighted"]}

## Artifacts

- JSON metrics: `reports/model_metrics.json`
- Text classification reports: `reports/*_classification_report.txt`
- Confusion matrices: `reports/figures/*.png`

## Notes

This is a simple baseline project rather than a highly tuned production system. It demonstrates a complete workflow: loading data, preprocessing, training, evaluation, and reporting.
"""

    (REPORTS_DIR / "final_report.md").write_text(report_text, encoding="utf-8")


def main() -> None:
    training_df = load_training_data()
    testing_df = load_testing_data()

    binary_x_train, binary_y_train = build_feature_matrix(
        training_df,
        target_column="label",
        columns_to_drop=["attack_cat", "id"],
    )
    binary_x_test, binary_y_test = build_feature_matrix(
        testing_df,
        target_column="label",
        columns_to_drop=["attack_cat", "id"],
    )

    multiclass_x_train, multiclass_y_train = build_feature_matrix(
        training_df,
        target_column="attack_cat",
        columns_to_drop=["label", "id"],
    )
    multiclass_x_test, multiclass_y_test = build_feature_matrix(
        testing_df,
        target_column="attack_cat",
        columns_to_drop=["label", "id"],
    )

    save_processed_splits(binary_x_train, binary_x_test, binary_y_train, binary_y_test, prefix="binary")
    save_processed_splits(
        multiclass_x_train,
        multiclass_x_test,
        multiclass_y_train,
        multiclass_y_test,
        prefix="attack_category",
    )

    results = {
        "binary_detection": train_and_evaluate(
            "binary_detection",
            binary_x_train,
            binary_y_train,
            binary_x_test,
            binary_y_test,
            multiclass=False,
        ),
        "attack_classification": train_and_evaluate(
            "attack_classification",
            multiclass_x_train,
            multiclass_y_train,
            multiclass_x_test,
            multiclass_y_test,
            multiclass=True,
        ),
    }

    save_json(results, REPORTS_DIR / "model_metrics.json")
    write_project_report(results)
    print(json.dumps(results, indent=2))
    print(f"Saved project artifacts under {PROCESSED_DATA_DIR} and {REPORTS_DIR}")


if __name__ == "__main__":
    main()
