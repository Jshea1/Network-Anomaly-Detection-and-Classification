from __future__ import annotations

import json

from network_anomaly_detection.config import PROCESSED_DATA_DIR
from network_anomaly_detection.data import (
    load_testing_data,
    load_training_data,
    summarize_dataframe,
)


def main() -> None:
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    profile = {
        "training_set": summarize_dataframe(load_training_data()),
        "testing_set": summarize_dataframe(load_testing_data()),
    }

    output_path = PROCESSED_DATA_DIR / "data_profile.json"
    output_path.write_text(json.dumps(profile, indent=2), encoding="utf-8")
    print(f"Wrote dataset profile to {output_path}")


if __name__ == "__main__":
    main()
