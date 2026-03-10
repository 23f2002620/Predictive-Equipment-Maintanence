import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings("ignore")

MRI_FEATURES = [
    "helium_pressure_psi", "cryogen_level_percent",
    "gradient_coil_temp_celsius", "gradient_coil_performance_score",
    "rf_coil_snr_db", "internal_temp_celsius", "vibration_amplitude_mm_s",
    "error_code_freq_7d", "scan_volume_per_day", "power_consumption_kwh",
    "cooling_system_temp_celsius",
]

CT_FEATURES = [
    "xray_tube_current_ma", "xray_tube_voltage_kv", "tube_heat_unit_percent",
    "detector_calibration_drift_score", "rotation_speed_rpm",
    "internal_temp_celsius", "vibration_amplitude_mm_s",
    "error_code_freq_7d", "scan_volume_per_day", "power_consumption_kwh",
    "cooling_system_temp_celsius",
]

MACHINE_FEATURES = {"MRI": MRI_FEATURES, "CT": CT_FEATURES}

Z_THRESHOLD = 2.0
ISOLATION_CONTAMINATION = 0.15


def compute_baseline(records: List[Dict], machine_type: str) -> Dict[str, Dict]:
    """30-day baseline statistics per sensor."""
    df = pd.DataFrame(records)
    features = MACHINE_FEATURES.get(machine_type, MRI_FEATURES)
    available = [f for f in features if f in df.columns]
    baseline = {}
    for feat in available:
        s = pd.to_numeric(df[feat], errors='coerce').dropna()
        if len(s) == 0:
            continue
        baseline[feat] = {
            "mean": float(s.mean()),
            "std": float(s.std()) if len(s) > 1 else 0.0,
            "min": float(s.min()),
            "max": float(s.max()),
            "p95": float(s.quantile(0.95)),
            "p05": float(s.quantile(0.05)),
        }
    return baseline


def zscore_anomaly_flags(records: List[Dict], baseline: Dict) -> List[Dict]:
    result = []
    for rec in records:
        flags = []
        for param, stats in baseline.items():
            val = rec.get(param)
            if val is None:
                continue
            try:
                val = float(val)
            except (TypeError, ValueError):
                continue
            std = stats["std"]
            if std == 0:
                continue
            z = abs((val - stats["mean"]) / std)
            if z > Z_THRESHOLD:
                direction = "HIGH" if val > stats["mean"] else "LOW"
                severity = "CRITICAL" if z > 4.0 else "WARNING" if z > 3.0 else "NOTICE"
                flags.append({
                    "parameter": param,
                    "value": round(val, 4),
                    "baseline_mean": round(stats["mean"], 4),
                    "z_score": round(z, 2),
                    "direction": direction,
                    "severity": severity,
                })
        result.append({
            "date": rec.get("date", ""),
            "flags": flags,
            "anomaly_count": len(flags),
        })
    return result


def isolation_forest_scores(records: List[Dict], machine_type: str) -> Tuple[List[int], List[float]]:
    df = pd.DataFrame(records)
    features = MACHINE_FEATURES.get(machine_type, MRI_FEATURES)
    available = [f for f in features if f in df.columns]
    X = df[available].apply(pd.to_numeric, errors='coerce').fillna(0).values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    iso = IsolationForest(contamination=ISOLATION_CONTAMINATION, random_state=42, n_estimators=100)
    preds = iso.fit_predict(X_scaled)
    scores = iso.decision_function(X_scaled)
    return preds.tolist(), [round(float(s), 4) for s in scores]


def detect_trend(records: List[Dict], param: str, window: int = 7) -> Dict:
    vals = []
    for r in records[-window:]:
        v = r.get(param)
        if v is not None:
            try:
                vals.append(float(v))
            except:
                pass
    if len(vals) < 3:
        return {"slope": 0.0, "direction": "STABLE"}
    x = np.arange(len(vals))
    slope = float(np.polyfit(x, vals, 1)[0])
    if abs(slope) < 0.001 * abs(np.mean(vals)):
        direction = "STABLE"
    elif slope > 0:
        direction = "INCREASING"
    else:
        direction = "DECREASING"
    return {"slope": round(slope, 4), "direction": direction, "current": round(vals[-1], 4)}


def full_anomaly_report(records: List[Dict], machine_type: str) -> Dict:
    baseline = compute_baseline(records, machine_type)
    zscore_flags = zscore_anomaly_flags(records, baseline)
    iso_preds, iso_scores = isolation_forest_scores(records, machine_type)

    # Trends on critical params
    critical_params = {
        "MRI": ["helium_pressure_psi", "cryogen_level_percent", "gradient_coil_performance_score", "error_code_freq_7d"],
        "CT":  ["tube_heat_unit_percent", "detector_calibration_drift_score", "error_code_freq_7d", "xray_tube_current_ma"],
    }
    trends = {p: detect_trend(records, p) for p in critical_params.get(machine_type, [])}

    # Chart-friendly merge
    chart_data = []
    for i, rec in enumerate(records):
        chart_data.append({
            "date": rec.get("date", ""),
            "anomaly_count": zscore_flags[i]["anomaly_count"],
            "flags": zscore_flags[i]["flags"],
            "iso_anomaly": iso_preds[i] == -1,
            "iso_score": iso_scores[i],
        })

    latest = zscore_flags[-1] if zscore_flags else {}
    return {
        "baseline": baseline,
        "chart_data": chart_data,
        "trends": trends,
        "summary": {
            "latest_flags": latest.get("flags", []),
            "latest_anomaly_count": latest.get("anomaly_count", 0),
            "total_anomaly_days_last7d": sum(1 for d in chart_data[-7:] if d["anomaly_count"] > 0),
            "iso_anomaly_days_last7d": sum(1 for d in chart_data[-7:] if d["iso_anomaly"]),
        }
    }
