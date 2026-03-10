from datetime import datetime, timedelta
from typing import Dict, List, Any
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.data.data_loader import (
    get_telemetry, get_vendors, get_scan_schedule, get_cost_impact, MACHINE_IDS, MACHINE_TYPES
)
from backend.models.anomaly_detection import full_anomaly_report
from backend.models.risk_classifier import classify_risk

_vendor_tickets:   List[Dict] = []
_reschedule_log:   List[Dict] = []
_notification_log: List[Dict] = []

def tool_classify_risk(machine_id: str) -> Dict:
    """classify_failure_risk tool."""
    records = get_telemetry(machine_id)
    machine_type = MACHINE_TYPES[machine_id]
    anomaly = full_anomaly_report(records, machine_type)

    latest = records[-1]
    tier_label = str(latest.get("risk_label", "Monitor"))
    if "Critical" in tier_label:
        tier_key = "Critical"
    elif "Schedule" in tier_label:
        tier_key = "Schedule"
    elif "Normal" in tier_label:
        tier_key = "Normal"
    else:
        tier_key = "Monitor"

    cost_rows = get_cost_impact(machine_id, tier_key)
    cost_row = cost_rows[0] if cost_rows else {}

    risk = classify_risk(latest, anomaly["summary"], cost_row)
    risk["machine_id"] = machine_id
    risk["machine_type"] = machine_type
    return risk

def tool_contact_vendor(machine_id: str, fault_summary: str, urgency: str, preferred_window: str) -> Dict:
    """contact_service_vendor tool."""
    vendors = get_vendors()
    machine_type = MACHINE_TYPES.get(machine_id, "")
    eligible = [v for v in vendors if v.get("vendor_id")]

    if machine_type == "MRI":
        vendor = next((v for v in eligible if "Siemens" in str(v.get("vendor_name", ""))), eligible[0] if eligible else {})
    else:
        vendor = next((v for v in eligible if "GE" in str(v.get("vendor_name", ""))), eligible[0] if eligible else {})

    ticket_id = f"TKT-{machine_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    record = {
        "ticket_id":            ticket_id,
        "machine_id":           machine_id,
        "vendor_id":            vendor.get("vendor_id"),
        "vendor_name":          vendor.get("vendor_name"),
        "contact_person":       vendor.get("contact_person"),
        "phone":                vendor.get("phone"),
        "email":                vendor.get("email"),
        "fault_summary":        fault_summary,
        "urgency":              urgency,
        "preferred_window":     preferred_window,
        "response_time_hours":  vendor.get("response_time_hours"),
        "hourly_rate_inr":      vendor.get("hourly_rate_inr"),
        "status":               "OPEN",
        "created_at":           datetime.now().isoformat(),
    }
    _vendor_tickets.append(record)
    return {"success": True, "ticket": record}

def tool_reschedule(appointment_id: str, new_slot: str, reason: str = "Scheduled maintenance overlap") -> Dict:
    """reschedule_appointment tool."""
    record = {
        "appointment_id":  appointment_id,
        "new_slot":        new_slot,
        "reason":          reason,
        "status":          "RESCHEDULED",
        "patient_notified": True,
        "rescheduled_at":  datetime.now().isoformat(),
    }
    _reschedule_log.append(record)
    return {"success": True, "record": record}

def tool_notify_team(machine_id: str, risk: Dict, recommended_action: str) -> Dict:
    """notify_engineering_team tool."""
    notif_id = f"NOTIF-{machine_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    cost = risk.get("cost_impact") or {}
    record = {
        "notification_id":    notif_id,
        "machine_id":         machine_id,
        "risk_tier":          risk.get("risk_label"),
        "failure_type":       risk.get("failure_description"),
        "days_to_failure":    risk.get("days_to_failure"),
        "confidence":         risk.get("confidence"),
        "recommended_action": recommended_action,
        "preventive_cost_inr":  cost.get("preventive_cost_inr"),
        "breakdown_cost_inr":   cost.get("total_breakdown_cost_inr"),
        "net_saving_inr":       cost.get("net_saving_inr"),
        "recipients":         ["radiology.head@hospital.in", "engineering@hospital.in"],
        "sent_at":            datetime.now().isoformat(),
    }
    _notification_log.append(record)
    return {"success": True, "notification": record}

def run_agent(machine_id: str) -> Dict:
    """Full agent pipeline for one machine."""
    actions: List[str] = []
    ts = lambda: datetime.now().strftime("%H:%M:%S")

    risk = tool_classify_risk(machine_id)
    tier = risk.get("risk_tier", 0)
    actions.append(f"[{ts()}] Risk assessed for {machine_id}: {risk['risk_emoji']} {risk['risk_label']} — {risk['failure_description']}")

    vendor_result = None
    reschedule_results = []
    notification_result = None

    if tier >= 2:  
        schedule = get_scan_schedule(machine_id)
        affected = [s for s in schedule if not s.get("rescheduled")]
        actions.append(f"[{ts()}] Retrieved {len(schedule)} appointments, {len(affected)} potentially affected")
        urgency = "CRITICAL" if tier >= 3 else "HIGH"
        days = risk.get("days_to_failure", "unknown")
        fault_summary = (
            f"{machine_id} | {risk['failure_description']} | "
            f"Days to failure: {days} | Confidence: {risk['confidence']*100:.0f}%"
        )
        vendor_result = tool_contact_vendor(
            machine_id=machine_id,
            fault_summary=fault_summary,
            urgency=urgency,
            preferred_window="Off-peak: 06:00–08:00 or overnight 22:00–06:00",
        )
        ticket_id = vendor_result["ticket"]["ticket_id"]
        vendor_name = vendor_result["ticket"]["vendor_name"]
        actions.append(f"[{ts()}] Service ticket {ticket_id} created with {vendor_name}")
        for appt in affected[:3]:
            existing_slot = appt.get("new_appointment_slot")
            if existing_slot:
                new_slot = str(existing_slot)
            else:
                new_slot = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d 10:00")

            res = tool_reschedule(
                appointment_id=appt.get("appointment_id", ""),
                new_slot=new_slot,
                reason="Predictive maintenance window",
            )
            reschedule_results.append(res["record"])
        if reschedule_results:
            actions.append(f"[{ts()}] Rescheduled {len(reschedule_results)} patient appointment(s)")

        cost = risk.get("cost_impact") or {}
        prev_cost  = cost.get("preventive_cost_inr", 0)
        breakdown  = cost.get("total_breakdown_cost_inr", 0)
        saving     = cost.get("net_saving_inr", 0)
        recommended = (
            f"⚠️ SUSPEND MACHINE — Emergency repair required. "
            f"Failure type: {risk['failure_description']}. "
            f"Preventive: ₹{prev_cost:,} vs Breakdown: ₹{breakdown:,} (Save ₹{saving:,})."
            if tier >= 3 else
            f"Schedule preventive maintenance within {days} days. "
            f"Preventive: ₹{prev_cost:,} vs Breakdown: ₹{breakdown:,} (Save ₹{saving:,})."
        )
        notification_result = tool_notify_team(machine_id, risk, recommended)
        actions.append(f"[{ts()}] Notifications sent to Radiology Head & Engineering team")

    else:  
        actions.append(f"[{ts()}] {machine_id} status: {risk['risk_emoji']} — No immediate action required. Monitoring continues.")

    return {
        "machine_id":    machine_id,
        "risk":          risk,
        "actions":       actions,
        "vendor_ticket": vendor_result,
        "reschedules":   reschedule_results,
        "notification":  notification_result,
        "completed":     True,
    }

def run_all_machines() -> Dict[str, Dict]:
    return {mid: run_agent(mid) for mid in MACHINE_IDS}

def get_agent_logs() -> Dict:
    return {
        "vendor_tickets":  _vendor_tickets,
        "reschedules":     _reschedule_log,
        "notifications":   _notification_log,
    }
