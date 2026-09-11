"""ShiftBridge Call Escalator — CALL-E hackathon MVP."""
from __future__ import annotations
import argparse
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from calle import CalleClient

@dataclass
class Incident:
    site: str
    line: str
    severity: str
    issue: str
    action_taken: str
    next_action: str
    deadline: str
    recipient_phone: str

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Incident":
        required = set(cls.__dataclass_fields__)
        missing = sorted(required - raw.keys())
        if missing:
            raise ValueError(f"Missing incident fields: {', '.join(missing)}")
        incident = cls(**{key: str(raw[key]).strip() for key in required})
        if incident.severity.upper() not in {"P1", "P2", "P3"}:
            raise ValueError("severity must be P1, P2, or P3")
        if not incident.recipient_phone.startswith("+"):
            raise ValueError("recipient_phone must use E.164 format")
        return incident

def build_call_task(i: Incident) -> str:
    return (
        f"You are ShiftBridge, an automated operational handover assistant. Call {i.recipient_phone}. "
        f"Report a {i.severity.upper()} issue at site {i.site}, line {i.line}: {i.issue}. "
        f"Action already taken: {i.action_taken}. Required next action: {i.next_action}. Deadline: {i.deadline}. "
        "Verify that the responsible person understands the issue, ask whether they accept ownership, "
        "capture their ETA or blocker, and determine whether a human supervisor needs escalation. "
        "Do not invent facts or commitments. If ownership is declined, mark escalation_required=true."
    )

RESULT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["reached_person", "understood_issue", "ownership", "eta_or_blocker", "escalation_required"],
    "properties": {
        "reached_person": {"type": "string", "enum": ["yes", "no", "unknown"]},
        "understood_issue": {"type": "string", "enum": ["yes", "no", "unknown"]},
        "ownership": {"type": "string", "enum": ["accepted", "declined", "unknown"]},
        "eta_or_blocker": {"type": "string"},
        "escalation_required": {"type": "boolean"}
    }
}

def run_incident(i: Incident) -> dict[str, Any]:
    api_key = os.environ.get("CALLE_API_KEY")
    if not api_key:
        raise RuntimeError("CALLE_API_KEY is not set")
    client = CalleClient(api_key=api_key)
    call = client.calls.create_and_wait(task=build_call_task(i), result_schema=RESULT_SCHEMA)
    return {
        "incident": asdict(i),
        "status": call.get("status"),
        "task_completed": call.get("task_completed"),
        "completion_confidence": call.get("completion_confidence"),
        "structured_result": call.get("structured_result"),
        "evidence": call.get("evidence")
    }

def main() -> None:
    parser = argparse.ArgumentParser(description="Escalate a shift handover incident by phone")
    parser.add_argument("incident", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    incident = Incident.from_dict(json.loads(args.incident.read_text(encoding="utf-8")))
    if args.dry_run:
        print(json.dumps({"incident": asdict(incident), "task": build_call_task(incident), "result_schema": RESULT_SCHEMA}, indent=2))
        return
    print(json.dumps(run_incident(incident), indent=2, ensure_ascii=False, default=str))

if __name__ == "__main__":
    main()
