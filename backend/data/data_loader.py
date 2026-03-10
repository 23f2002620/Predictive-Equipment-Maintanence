import json
import os
from typing import Dict, List, Any

DATA_DIR = os.path.join(os.path.dirname(__file__))

def _load(filename: str) -> Any:
    path = os.path.join(DATA_DIR, filename)
    with open(path, "r") as f:
        return json.load(f)

def get_telemetry(machine_id: str) -> List[Dict]:
    """Returns 30-day telemetry list for MRI_01 or CT_01."""
    if machine_id == "MRI_01":
        return _load("telemetry_mri.json")
    elif machine_id == "CT_01":
        return _load("telemetry_ct.json")
    raise ValueError(f"Unknown machine_id: {machine_id}")

def get_all_telemetry() -> Dict[str, List[Dict]]:
    return {
        "MRI_01": _load("telemetry_mri.json"),
        "CT_01":  _load("telemetry_ct.json"),
    }

def get_baselines() -> List[Dict]:
    return _load("baselines.json")

def get_baselines_by_machine(machine_type: str) -> List[Dict]:
    all_bl = get_baselines()
    return [b for b in all_bl if b.get("Machine Type") in (machine_type, "Both")]

def get_vendors() -> List[Dict]:
    return _load("vendors.json")

def get_scan_schedule(machine_id: str = None) -> List[Dict]:
    schedule = _load("schedule.json")
    if machine_id:
        return [s for s in schedule if s.get("machine_id") == machine_id]
    return schedule

def get_cost_impact(machine_id: str = None, risk_tier_label: str = None) -> List[Dict]:
    cost = _load("cost_impact.json")
    cost = [c for c in cost if c.get("machine_id") is not None] 
    if machine_id:
        cost = [c for c in cost if c.get("machine_id") == machine_id]
    if risk_tier_label:
        cost = [c for c in cost if risk_tier_label in str(c.get("risk_tier", ""))]
    return cost


MACHINE_IDS = ["MRI_01", "CT_01"]
MACHINE_TYPES = {"MRI_01": "MRI", "CT_01": "CT"}
