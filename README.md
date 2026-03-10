# MediWatch — Predictive Equipment Maintenance
## GKM_11 · GLITCHCON 2.0 · Team FASTENERS

> Autonomous AI agent that predicts MRI/CT scanner failures before they happen —
> eliminating reactive breakdowns, protecting patient schedules, and saving ₹50L+ annually.

---

## Tech Stack
| Layer              | Technology                              |
|--------------------|------------------------------------------|
| Agent Orchestration| LangGraph (state machine)               |
| Anomaly Detection  | Isolation Forest + Rolling Z-Score (scikit-learn + Pandas) |
| Risk Classification| XGBoost-ready / Rule-based classifier   |
| Frontend           | Vue 3 + Tailwind CSS + SVG charts       |
| Backend            | FastAPI (Python)                        |
| Database           | JSON / SQLite (pluggable)               |
| Dataset            | GKM11_Predictive_Maintenance_Dataset.xlsx |

---

## Quick Start

### 1. Backend
```bash
cd predictive-maintenance/backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 2. Frontend
```bash
cd predictive-maintenance/frontend
npm install
npm run dev        # dev mode: http://localhost:5173
npm run build      # production build → dist/
```

### 3. Production (serve frontend from FastAPI)
```bash
cd frontend && npm run build
cd ../backend
uvicorn main:app --host 0.0.0.0 --port 8000
# Visit: http://localhost:8000
```

---

## Agent Pipeline (LangGraph)
```
Telemetry Ingest
    ↓
Isolation Forest + Z-Score Anomaly Detection
    ↓
XGBoost Risk Classification → 🟢 Normal / 🟡 Monitor / 🔴 Schedule / ⚫ Critical
    ↓ (if 🔴 or ⚫)
contact_service_vendor()  →  Schedule technician
    ↓
reschedule_appointment()  →  Move conflicting patient scans
    ↓
notify_engineering_team() →  Alert Radiology Head + Engineering
    ↓
cost_calculator()         →  Preventive vs Breakdown ROI
```

---

## API Endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | /api/dashboard | Full dashboard data (all machines) |
| GET | /api/telemetry/{machine_id} | 30-day telemetry |
| GET | /api/anomalies/{machine_id} | Anomaly detection report |
| GET | /api/risk/{machine_id} | Risk classification |
| GET | /api/chart/{machine_id}/{sensor} | Sensor chart data |
| GET | /api/schedule | All patient appointments |
| GET | /api/vendors | Vendor directory |
| GET | /api/cost/{machine_id} | Cost impact analysis |
| POST | /api/agent/run/{machine_id} | Run agent for one machine |
| POST | /api/agent/run-all | Run agent for all machines |
| GET | /api/agent/logs | Agent activity log |

---

## Dataset
The app uses real data from `GKM11_Predictive_Maintenance_Dataset.xlsx`:
- **MRI_01**: 30-day telemetry with embedded cryogen leak degradation pattern (escalates to ⚫ Critical day 30)
- **CT_01**: 30-day telemetry with calibration drift + tube burnout pattern (escalates to ⚫ Critical day 30)
- **Baselines**: Normal operating ranges for 20 sensor parameters
- **Vendors**: Siemens Healthineers + GE Healthcare Biomedical
- **Schedule**: 20 patient appointments (10 per machine, 7-day window)
- **Cost Impact**: Preventive vs breakdown cost at each risk tier

---