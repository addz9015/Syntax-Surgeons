from __future__ import annotations

import os
from typing import Any, Dict, List

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from vitaledge_core import estimate_risk, infer_conflict, load_output_data, load_raw_data

app = FastAPI(title="VitalEdge+ API", version="1.0.0")


def _get_allowed_origins() -> List[str]:
    raw_origins = os.getenv("VITALEDGE_CORS_ORIGINS", "*")
    return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]


ALLOWED_ORIGINS = _get_allowed_origins()


def _load_raw() -> Dict[str, pd.DataFrame]:
    return load_raw_data()


def _load_outputs() -> Dict[str, pd.DataFrame]:
    try:
        return load_output_data()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _clean_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _clean_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_clean_value(item) for item in value]
    if isinstance(value, tuple):
        return [_clean_value(item) for item in value]
    if isinstance(value, np.generic):
        return value.item()
    if value is None:
        return None
    if pd.isna(value):
        return None
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def _normalize_text(value: Any) -> str:
    return str(value or "").strip().lower()


app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=ALLOWED_ORIGINS != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/kpis")
def kpis() -> List[Dict[str, object]]:
    outputs = _load_outputs()
    return _clean_value(outputs["kpis"].to_dict(orient="records"))


@app.get("/model-metrics")
def model_metrics() -> Dict[str, object]:
    outputs = _load_outputs()
    return _clean_value(outputs["model"].iloc[0].to_dict())


@app.get("/data-quality")
def data_quality() -> Dict[str, object]:
    outputs = _load_outputs()
    return _clean_value(outputs["quality"].iloc[0].to_dict())


@app.get("/doctor-risk")
def doctor_risk(limit: int = 50) -> List[Dict[str, object]]:
    outputs = _load_outputs()
    return _clean_value(outputs["doctors"].head(limit).to_dict(orient="records"))


@app.get("/clusters")
def clusters() -> List[Dict[str, object]]:
    outputs = _load_outputs()
    return _clean_value(outputs["clusters"].to_dict(orient="records"))


@app.get("/explanations")
def explanations(limit: int = 12) -> List[Dict[str, object]]:
    outputs = _load_outputs()
    return _clean_value(outputs["explanations"].head(limit).to_dict(orient="records"))


@app.get("/patients")
def patients(limit: int = 500) -> List[Dict[str, object]]:
    outputs = _load_outputs()
    return _clean_value(outputs["patients"].head(limit).to_dict(orient="records"))


@app.get("/medicines")
def medicines(limit: int = 500) -> List[Dict[str, object]]:
    raw = _load_raw()
    catalog = raw["medicines"][["Medicine_ID", "Medicine_Name", "Allergen_Class", "Requires_Allergy_Check"]].copy()
    return _clean_value(catalog.head(limit).to_dict(orient="records"))


@app.get("/patients/{patient_id}")
def patient_profile(patient_id: str) -> Dict[str, object]:
    outputs = _load_outputs()
    raw = _load_raw()

    p = outputs["patients"]
    row = p[p["Patient_ID"].astype(str) == patient_id]
    if row.empty:
        raise HTTPException(status_code=404, detail="Patient not found")

    allergies = raw["allergies"][raw["allergies"]["Patient_ID"].astype(str) == patient_id]
    rx = raw["prescriptions"][raw["prescriptions"]["Patient_ID"].astype(str) == patient_id]

    return _clean_value({
        "patient": row.iloc[0].to_dict(),
        "allergies": allergies.to_dict(orient="records"),
        "prescriptions": rx.head(20).to_dict(orient="records"),
    })


@app.get("/simulate")
def simulate(patient_id: str, medicine_id: str) -> Dict[str, object]:
    outputs = _load_outputs()
    raw = _load_raw()

    p = outputs["patients"]
    row = p[p["Patient_ID"].astype(str) == patient_id]
    if row.empty:
        raise HTTPException(status_code=404, detail="Patient not found")

    med = raw["medicines"][raw["medicines"]["Medicine_ID"].astype(str) == medicine_id]
    if med.empty:
        raise HTTPException(status_code=404, detail="Medicine not found")

    conflict, reason = infer_conflict(patient_id, medicine_id, raw)
    abs_score = float(row.iloc[0]["Allergy_Burden_Score"])
    requires = str(med.iloc[0].get("Requires_Allergy_Check", "")).strip().lower() in ["true", "1", "yes"]
    risk = estimate_risk(abs_score, conflict, requires)

    explanations = outputs["explanations"].head(3).to_dict(orient="records")
    alternatives = raw["medicines"][
        (raw["medicines"]["Allergen_Class"].astype(str) != str(med.iloc[0].get("Allergen_Class", "")))
        & (raw["medicines"]["Requires_Allergy_Check"].astype(str).str.lower().isin(["false", "0", "no"]))
    ]

    alt_row = alternatives.sample(1, random_state=42).iloc[0].to_dict() if len(alternatives) > 0 else None

    return _clean_value({
        "patient_id": patient_id,
        "medicine_id": medicine_id,
        "conflict": {"conflict": conflict, "reason": reason},
        "risk_score": risk,
        "abs_score": abs_score,
        "top_explanations": explanations,
        "recommended_alternative": alt_row,
    })


@app.post("/simulate-custom")
def simulate_custom(payload: Dict[str, Any]) -> Dict[str, object]:
    medicine_name = str(payload.get("medicine_name", "")).strip()
    medicine_allergen_class = str(payload.get("medicine_allergen_class", "")).strip()
    requires_allergy_check = bool(payload.get("requires_allergy_check", True))
    patient_label = str(payload.get("patient_label", "Custom patient")).strip() or "Custom patient"

    allergies_raw = payload.get("allergies", [])
    if not isinstance(allergies_raw, list):
        raise HTTPException(status_code=400, detail="allergies must be an array of allergy objects")
    if not medicine_name:
        raise HTTPException(status_code=400, detail="medicine_name is required")
    if not medicine_allergen_class:
        raise HTTPException(status_code=400, detail="medicine_allergen_class is required")

    normalized_med_class = _normalize_text(medicine_allergen_class)

    normalized_allergies: List[Dict[str, str]] = []
    critical_count = 0
    active_class_matches = 0
    history_class_matches = 0

    for entry in allergies_raw:
        if not isinstance(entry, dict):
            continue
        allergen_name = str(entry.get("allergen_name", "")).strip()
        allergen_class = str(entry.get("allergen_class", "")).strip()
        severity = str(entry.get("severity", "UNKNOWN")).strip().upper() or "UNKNOWN"
        status = str(entry.get("status", "current")).strip().lower() or "current"

        if not allergen_name and not allergen_class:
            continue

        normalized_allergies.append(
            {
                "allergen_name": allergen_name,
                "allergen_class": allergen_class,
                "severity": severity,
                "status": status,
            }
        )

        if severity in {"SEVERE", "CRITICAL"}:
            critical_count += 1

        class_match = _normalize_text(allergen_class) == normalized_med_class
        if class_match and status in {"current", "active"}:
            active_class_matches += 1
        elif class_match:
            history_class_matches += 1

    if not normalized_allergies:
        raise HTTPException(status_code=400, detail="At least one allergy record is required")

    if active_class_matches > 0:
        conflict = "CRITICAL"
        reason = f"Direct active allergen-class match: {medicine_allergen_class}"
    elif history_class_matches > 0:
        conflict = "ADVISORY"
        reason = f"Historical allergen-class match: {medicine_allergen_class}"
    elif critical_count > 0 and requires_allergy_check:
        conflict = "WARNING"
        reason = "No direct class match, but patient has severe allergy history and medicine requires checks"
    else:
        conflict = "NONE"
        reason = "No class conflict detected in user-provided allergy profile"

    supplied_abs = payload.get("abs_score")
    if supplied_abs is not None:
        try:
            abs_score = float(supplied_abs)
        except (TypeError, ValueError) as exc:
            raise HTTPException(status_code=400, detail="abs_score must be numeric") from exc
    else:
        baseline = 15.0
        baseline += min(len(normalized_allergies), 6) * 8.0
        baseline += critical_count * 6.0
        abs_score = min(95.0, baseline)

    risk = estimate_risk(abs_score, conflict, requires_allergy_check)

    return _clean_value(
        {
            "patient_id": patient_label,
            "medicine_name": medicine_name,
            "medicine_allergen_class": medicine_allergen_class,
            "conflict": {"conflict": conflict, "reason": reason},
            "risk_score": risk,
            "abs_score": abs_score,
            "allergies_used": normalized_allergies,
        }
    )
