# Network-Anomaly-Detection-and-Classification

This project aims to build a network anomaly detection and classification system using the [UNSW-NB15 dataset](https://www.kaggle.com/datasets/mrwellsdavid/unsw-nb15). The goal is to analyze network traffic data and determine whether activity is normal or malicious.

The dataset includes labeled examples of normal behavior and multiple attack categories, which makes it a strong fit for a pattern recognition project. It also includes messy, incomplete, and noisy data, so part of the project is demonstrating practical data cleaning and preprocessing.

The initial modeling plan is to:

1. Inspect and clean the raw data.
2. Handle missing values and noisy records.
3. Select useful features.
4. Train a baseline classifier such as a Decision Tree or K-Nearest Neighbors model.
5. Evaluate results with metrics such as accuracy, precision, recall, and F1-score.

## Current Project Layout

```text
data/
  raw/        Original Kaggle files
  processed/  Derived artifacts and cleaned outputs
notebooks/    Exploration notebooks
reports/      Figures or written outputs
src/          Reusable Python code
```

## Quick Start

1. Create and activate a virtual environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the starter data profiling script:

   ```powershell
   $env:PYTHONPATH="src"; python -m network_anomaly_detection.profile_data
   ```

This writes a first-pass summary to `data/processed/data_profile.json`, which is a good place to start before building a classifier.
