from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

def _find_root() -> Path:
    # Walk up from this file until we find a directory containing patients.csv,
    # which handles both local (file next to data) and Vercel (file in api/ subfolder).
    candidate = Path(__file__).resolve().parent
    for _ in range(4):
        if (candidate / "patients.csv").exists():
            return candidate
        candidate = candidate.parent
    # Fallback: same directory as this file
    return Path(__file__).resolve().parent


ROOT = _find_root()
OUT = ROOT / "outputs"


def load_raw_data() -> Dict[str, pd.DataFrame]:
    return {
        "patients": pd.read_csv(ROOT / "patients.csv"),
        "allergies": pd.read_csv(ROOT / "allergies.csv"),
        "medicines": pd.read_csv(ROOT / "medicines.csv"),
        "prescriptions": pd.read_csv(ROOT / "prescriptions.csv"),
        "labs": pd.read_csv(ROOT / "lab_results.csv"),
        "events": pd.read_csv(ROOT / "allergy_events.csv"),
    }


def load_output_data() -> Dict[str, pd.DataFrame]:
    required = {
        "kpis": OUT / "kpi_summary.csv",
        "quality": OUT / "data_quality_scorecard.csv",
        "model": OUT / "model_metrics.csv",
        "patients": OUT / "patient_intelligence.csv",
        "doctors": OUT / "doctor_risk_profile.csv",
        "clusters": OUT / "cluster_summary.csv",
        "explanations": OUT / "high_risk_explanations.csv",
    }
    missing = [path.name for path in required.values() if not path.exists()]
    if missing:
        missing_list = ", ".join(missing)
        raise FileNotFoundError(f"Missing output files: {missing_list}. Run vitaledge_prd_pipeline.py first.")
    return {name: pd.read_csv(path) for name, path in required.items()}


def to_bool(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .str.strip()
        .str.lower()
        .map({"true": True, "false": False, "1": True, "0": False, "yes": True, "no": False})
        .fillna(False)
    )


def split_pipe_values(value: object) -> List[str]:
    if pd.isna(value):
        return []
    text = str(value).replace(";", "|")
    return [part.strip() for part in text.split("|") if part.strip()]


def infer_conflict(patient_id: str, medicine_id: str, raw: Dict[str, pd.DataFrame]) -> Tuple[str, str]:
    allergies = raw["allergies"].copy()
    medicines = raw["medicines"].copy()

    if "Is_Current" in allergies.columns:
        allergies["Is_Current"] = to_bool(allergies["Is_Current"])

    active = allergies[(allergies["Patient_ID"].astype(str) == patient_id) & (allergies["Is_Current"] == True)]
    history = allergies[allergies["Patient_ID"].astype(str) == patient_id]

    med_row = medicines[medicines["Medicine_ID"].astype(str) == medicine_id]
    if med_row.empty:
        return "NONE", "Medicine not found in catalog"

    med = med_row.iloc[0]
    med_class = str(med.get("Allergen_Class", "")).strip()
    cross = set(split_pipe_values(med.get("Cross_Reactive_With", "")))
    contraindicated = set(split_pipe_values(med.get("Contraindicated_Allergies", "")))

    active_classes = set(active["Allergen_Class"].dropna().astype(str))
    history_classes = set(history["Allergen_Class"].dropna().astype(str))

    if med_class and med_class in active_classes:
        return "CRITICAL", f"Direct active allergen-class match: {med_class}"
    if cross.intersection(active_classes) or contraindicated.intersection(active_classes):
        return "WARNING", "Cross-reactive or contraindicated class matched an active allergy"
    if med_class and med_class in history_classes:
        return "ADVISORY", f"Historical class match found: {med_class}"
    return "NONE", "No class conflict in current allergy profile"


def estimate_risk(abs_score: float, conflict: str, requires_check: bool) -> float:
    base = min(0.95, max(0.01, abs_score / 100.0))
    bump = {"NONE": 0.00, "ADVISORY": 0.08, "WARNING": 0.20, "CRITICAL": 0.35}.get(conflict, 0.0)
    check_boost = 0.08 if requires_check else -0.03
    return float(np.clip(base + bump + check_boost, 0.01, 0.99))


def risk_color(conflict: str) -> str:
    return {
        "CRITICAL": "#cf3f2e",
        "WARNING": "#f18f01",
        "ADVISORY": "#ba8f2a",
        "NONE": "#2f855a",
    }.get(conflict, "#2563eb")