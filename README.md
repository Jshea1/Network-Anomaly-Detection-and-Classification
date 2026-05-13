# Network Anomaly Detection and Classification

This project uses the UNSW-NB15 dataset to build a simple network anomaly detection and attack classification system. The goal is to identify whether network traffic is normal or malicious, then classify the traffic into an attack category when possible.

The project is intentionally modest and complete. It includes dataset inspection, preprocessing, model training, evaluation, and generated report artifacts.

## Dataset

Source: [UNSW-NB15 on Kaggle](https://www.kaggle.com/datasets/mrwellsdavid/unsw-nb15)

The project uses the official training and testing CSV files located in `data/raw/archive/`:

- `UNSW_NB15_training-set.csv`
- `UNSW_NB15_testing-set.csv`

## Project Structure

```text
data/
  raw/         Original Kaggle files
  processed/   Saved train/test feature splits and data summaries
reports/
  figures/     Confusion matrix images
src/
  network_anomaly_detection/
    config.py
    data.py
    profile_data.py
    train_models.py
```

## Method

The workflow is:

1. Load the UNSW-NB15 training and testing sets.
2. Profile the dataset and inspect label distributions.
3. Build preprocessing pipelines:
   - median imputation for numeric columns
   - most-frequent imputation for categorical columns
   - one-hot encoding for categorical features
4. Train Decision Tree models for:
   - binary anomaly detection using `label`
   - multi-class attack classification using `attack_cat`
5. Evaluate model performance using accuracy, precision, recall, and F1-score.

## Results

Baseline results from the current pipeline:

- Binary anomaly detection accuracy: `0.89`
- Binary anomaly detection weighted F1-score: `0.893`
- Attack classification accuracy: `0.7484`
- Attack classification weighted F1-score: `0.7477`

## How To Run

Install dependencies:

```powershell
pip install -r requirements.txt
```

Generate a dataset profile:

```powershell
python -m network_anomaly_detection.profile_data
```

Train the models and generate final artifacts:

```powershell
python -m network_anomaly_detection.train_models
```

## Output Files

Important generated outputs:

- `data/processed/data_profile.json`
- `data/processed/binary_x_train.csv`
- `data/processed/binary_x_test.csv`
- `data/processed/attack_category_x_train.csv`
- `data/processed/attack_category_x_test.csv`
- `reports/model_metrics.json`
- `reports/final_report.md`
- `reports/binary_detection_classification_report.txt`
- `reports/attack_classification_classification_report.txt`
- `reports/figures/binary_detection_confusion_matrix.png`
- `reports/figures/attack_classification_confusion_matrix.png`
