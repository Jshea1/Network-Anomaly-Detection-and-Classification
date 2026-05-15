# Final Project Summary

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

- Accuracy: 0.89
- Precision (weighted): 0.9128
- Recall (weighted): 0.89
- F1-score (weighted): 0.893

### Attack Category Classification

- Accuracy: 0.7484
- Precision (weighted): 0.7958
- Recall (weighted): 0.7484
- F1-score (weighted): 0.7477

## Artifacts

- JSON metrics: `reports/model_metrics.json`
- Text classification reports: `reports/*_classification_report.txt`
- Confusion matrices: `reports/figures/*.png`

## How to Run

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   2. Open the notebook:
   `AAI_646_Final_Project (1).ipynb`

3. Run all cells sequentially.

4. Generated reports and metrics will appear in the reports folder.
## Notes
This is a simple baseline project rather than a highly tuned production system. It demonstrates a complete workflow: loading data, preprocessing, training, evaluation, and reporting.
