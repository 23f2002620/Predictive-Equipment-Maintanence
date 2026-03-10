import sys, os, math, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from datetime import datetime

def sanitize(obj):
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    if isinstance(obj, dict):
        return {k: sanitize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize(v) for v in obj]
    return obj

def ok(data) -> JSONResponse:
    return JSONResponse(content=sanitize(data))

from backend.data.data_loader import (
    get_telemetry, get_all_telemetry, get_baselines, get_baselines_by_machine,
    get_vendors, get_scan_schedule, get_cost_impact, MACHINE_IDS, MACHINE_TYPES
)
from backend.models.anomaly_detection import full_anomaly_report, compute_baseline
from backend.models.risk_classifier import classify_risk
from backend.agent.agent import run_agent, run_all_machines, get_agent_logs, tool_classify_risk

app = FastAPI(
    title="MediWatch — Predictive Equipment Maintenance API",
    description="GKM_11 · GLITCHCON 2.0 · Team FASTENERS",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def _resolve_tier_key(risk_label: str) -> str:
    label = str(risk_label)
    if "Critical" in label:
        return "Critical"
    if "Schedule" in label:
        return "Schedule"
    if "Monitor" in label:
        return "Monitor"
    return "Normal"

@app.get("/api/health")
def health():
    return ok({"status": "ok", "ts": datetime.now().isoformat()})

@app.get("/api/dashboard")
def dashboard():
    """Single call for the main dashboard — returns full state for all machines."""
    machines = []
    for mid in MACHINE_IDS:
        mt = MACHINE_TYPES[mid]
        records = get_telemetry(mid)
        anomaly = full_anomaly_report(records, mt)

        latest = records[-1]
        tier_key = _resolve_tier_key(str(latest.get("risk_label", "")))
        cost_rows = get_cost_impact(mid, tier_key)
        cost_row = cost_rows[0] if cost_rows else {}

        risk = classify_risk(latest, anomaly["summary"], cost_row)
        schedule = get_scan_schedule(mid)

        machines.append({
            "machine_id":      mid,
            "machine_type":    mt,
            "manufacturer":    latest.get("manufacturer"),
            "model":           latest.get("model_number"),
            "age_years":       latest.get("machine_age_years"),
            "latest":          latest,
            "risk":            risk,
            "anomaly_summary": anomaly["summary"],
            "trends":          anomaly["trends"],
            "appointments":    schedule,
            "upcoming_count":  len(schedule),
        })
    return ok({"machines": machines, "generated_at": datetime.now().isoformat()})

@app.get("/api/telemetry/{machine_id}")
def get_telemetry_endpoint(machine_id: str, days: int = 30):
    if machine_id not in MACHINE_IDS:
        raise HTTPException(404, f"Unknown machine: {machine_id}")
    records = get_telemetry(machine_id)
    return ok({"machine_id": machine_id, "records": records[-days:], "count": min(days, len(records))})


@app.get("/api/telemetry/{machine_id}/latest")
def latest_telemetry(machine_id: str):
    if machine_id not in MACHINE_IDS:
        raise HTTPException(404, f"Unknown machine: {machine_id}")
    return ok(get_telemetry(machine_id)[-1])

@app.get("/api/chart/{machine_id}/{sensor}")
def sensor_chart(machine_id: str, sensor: str):
    if machine_id not in MACHINE_IDS:
        raise HTTPException(404)
    records = get_telemetry(machine_id)
    mt = MACHINE_TYPES[machine_id]
    baseline = compute_baseline(records, mt)
    b = baseline.get(sensor, {})
    data = []
    for r in records:
        val = r.get(sensor)
        try:
            val = float(val) if val is not None else None
        except Exception:
            val = None
        data.append({
            "date":  r.get("date"),
            "value": round(val, 4) if val is not None else None,
            "mean":  round(b.get("mean", 0), 4),
            "upper": round(b.get("mean", 0) + 2 * b.get("std", 0), 4),
            "lower": round(b.get("mean", 0) - 2 * b.get("std", 0), 4),
        })
    return ok({"machine_id": machine_id, "sensor": sensor, "data": data})

@app.get("/api/anomalies/{machine_id}")
def anomalies(machine_id: str):
    if machine_id not in MACHINE_IDS:
        raise HTTPException(404)
    records = get_telemetry(machine_id)
    mt = MACHINE_TYPES[machine_id]
    report = full_anomaly_report(records, mt)
    return ok({"machine_id": machine_id, **report})

@app.get("/api/risk/{machine_id}")
def risk_endpoint(machine_id: str):
    if machine_id not in MACHINE_IDS:
        raise HTTPException(404)
    return ok(tool_classify_risk(machine_id))

@app.get("/api/schedule")
def schedule_all():
    return ok({"schedule": get_scan_schedule()})

@app.get("/api/schedule/{machine_id}")
def schedule_machine(machine_id: str):
    return ok({"machine_id": machine_id, "appointments": get_scan_schedule(machine_id)})

@app.get("/api/vendors")
def vendors():
    return ok({"vendors": get_vendors()})

@app.get("/api/cost")
def cost_all():
    return ok({"cost_impact": get_cost_impact()})

@app.get("/api/cost/{machine_id}")
def cost_machine(machine_id: str):
    return ok({"machine_id": machine_id, "cost_impact": get_cost_impact(machine_id)})

@app.post("/api/agent/run/{machine_id}")
def agent_run(machine_id: str):
    if machine_id not in MACHINE_IDS:
        raise HTTPException(404)
    return ok(run_agent(machine_id))

@app.post("/api/agent/run-all")
def agent_run_all():
    return ok({"results": run_all_machines()})

@app.get("/api/agent/logs")
def agent_logs():
    return ok(get_agent_logs())

_frontend_dist = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
if os.path.isdir(_frontend_dist):
    _assets = os.path.join(_frontend_dist, "assets")
    if os.path.isdir(_assets):
        app.mount("/assets", StaticFiles(directory=_assets), name="assets")

    @app.get("/", include_in_schema=False)
    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_spa(full_path: str = ""):
        idx = os.path.join(_frontend_dist, "index.html")
        return FileResponse(idx) if os.path.exists(idx) else {"msg": "Build frontend first: cd frontend && npm run build"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
