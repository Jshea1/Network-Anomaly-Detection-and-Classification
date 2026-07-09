from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = PROJECT_ROOT / "models"

# One real record from the UNSW-NB15 testing set 
SAMPLE_INPUT = {
    "dur": 0.121478,
    "proto": "tcp",
    "service": "-",
    "state": "FIN",
    "spkts": 6,
    "dpkts": 4,
    "sbytes": 258,
    "dbytes": 172,
    "rate": 74.08749,
    "sttl": 252,
    "dttl": 254,
    "sload": 14158.94238,
    "dload": 8495.365234,
    "sloss": 0,
    "dloss": 0,
    "sinpkt": 24.2956,
    "dinpkt": 8.375,
    "sjit": 30.177547,
    "djit": 11.830604,
    "swin": 255,
    "stcpb": 621772692,
    "dtcpb": 2202533631,
    "dwin": 255,
    "tcprtt": 0,
    "synack": 0,
    "ackdat": 0,
    "smean": 43,
    "dmean": 43,
    "trans_depth": 0,
    "response_body_len": 0,
    "ct_srv_src": 1,
    "ct_state_ttl": 0,
    "ct_dst_ltm": 1,
    "ct_src_dport_ltm": 1,
    "ct_dst_sport_ltm": 1,
    "ct_dst_src_ltm": 1,
    "is_ftp_login": 0,
    "ct_ftp_cmd": 0,
    "ct_flw_http_mthd": 0,
    "ct_src_ltm": 1,
    "ct_srv_dst": 1,
    "is_sm_ips_ports": 0,
}


def main() -> None:
    sample = pd.DataFrame([SAMPLE_INPUT])

    binary_model = joblib.load(MODELS_DIR / "binary_detection_pipeline.joblib")
    binary_prediction = binary_model.predict(sample)[0]
    binary_label = "Attack" if int(binary_prediction) == 1 else "Normal"
    print(f"Binary detection prediction: {binary_label} (raw label={binary_prediction})")

    attack_model = joblib.load(MODELS_DIR / "attack_classification_pipeline.joblib")
    attack_prediction = attack_model.predict(sample)[0]
    print(f"Attack category prediction: {attack_prediction}")


if __name__ == "__main__":
    main()
