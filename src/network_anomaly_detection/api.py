"""Minimal FastAPI wrapper around the trained anomaly detection pipelines.

Run locally with:
    uvicorn network_anomaly_detection.api:app --reload

Then open http://127.0.0.1:8000/docs for the interactive Swagger UI.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

from network_anomaly_detection.config import PROJECT_ROOT

MODELS_DIR = PROJECT_ROOT / "models"

models: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    models["binary"] = joblib.load(MODELS_DIR / "binary_detection_pipeline.joblib")
    models["attack_category"] = joblib.load(MODELS_DIR / "attack_classification_pipeline.joblib")
    yield
    models.clear()


app = FastAPI(
    title="Network Anomaly Detection API",
    description="Classifies network traffic records (UNSW-NB15 features) as Normal or Attack.",
    version="0.1.0",
    lifespan=lifespan,
)


class NetworkTrafficFeatures(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
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
        }
    )

    dur: float
    proto: str
    service: str
    state: str
    spkts: int
    dpkts: int
    sbytes: int
    dbytes: int
    rate: float
    sttl: int
    dttl: int
    sload: float
    dload: float
    sloss: int
    dloss: int
    sinpkt: float
    dinpkt: float
    sjit: float
    djit: float
    swin: int
    stcpb: int
    dtcpb: int
    dwin: int
    tcprtt: float
    synack: float
    ackdat: float
    smean: int
    dmean: int
    trans_depth: int
    response_body_len: int
    ct_srv_src: int
    ct_state_ttl: int
    ct_dst_ltm: int
    ct_src_dport_ltm: int
    ct_dst_sport_ltm: int
    ct_dst_src_ltm: int
    is_ftp_login: int
    ct_ftp_cmd: int
    ct_flw_http_mthd: int
    ct_src_ltm: int
    ct_srv_dst: int
    is_sm_ips_ports: int


class PredictionResponse(BaseModel):
    label: str = Field(description="'Normal' or 'Attack'")
    label_confidence: float
    attack_category: str
    attack_category_confidence: float


@app.get("/")
def root() -> dict:
    return {"message": "Network Anomaly Detection API is running. See /docs for usage."}


@app.post("/predict", response_model=PredictionResponse)
def predict(features: NetworkTrafficFeatures) -> PredictionResponse:
    sample = pd.DataFrame([features.model_dump()])

    binary_model = models["binary"]
    binary_pred = int(binary_model.predict(sample)[0])
    binary_proba = binary_model.predict_proba(sample)[0]
    label = "Attack" if binary_pred == 1 else "Normal"

    attack_model = models["attack_category"]
    attack_pred = str(attack_model.predict(sample)[0])
    attack_proba = attack_model.predict_proba(sample)[0]
    attack_classes = list(attack_model.classes_)

    return PredictionResponse(
        label=label,
        label_confidence=float(binary_proba[binary_pred]),
        attack_category=attack_pred,
        attack_category_confidence=float(attack_proba[attack_classes.index(attack_pred)]),
    )
