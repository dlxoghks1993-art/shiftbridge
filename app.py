"""ShiftBridge Handover Assurance — CALL-E hackathon MVP."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from dataclasses import asdict, dataclass, replace
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
    escalation_phones: list[str] | None = None

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Incident":
        required = {
            "site",
            "line",
            "severity",
            "issue",
            "action_taken",
            "next_action",
            "deadline",
            "recipient_phone",
        }
        missing = sorted(required - raw.keys())
        if missing:
            raise ValueError(f"Missing incident fields: {', '.join(missing)}")
        escalation_phones = raw.get("escalation_phones") or []
        if not isinstance(escalation_phones, list):
            raise ValueError("escalation_phones must be a list")
        incident = cls(
            site=str(raw["site"]).strip(),
            line=str(raw["line"]).strip(),
            severity=str(raw["severity"]).strip(),
            issue=str(raw["issue"]).strip(),
            action_taken=str(raw["action_taken"]).strip(),
            next_action=str(raw["next_action"]).strip(),
            deadline=str(raw["deadline"]).strip(),
            recipient_phone=str(raw["recipient_phone"]).strip(),
            escalation_phones=[str(v).strip() for v in escalation_phones],
        )
        if incident.severity.upper() not in {"P1", "P2", "P3"}:
            raise ValueError("severity must be P1, P2, or P3")
        for phone in [incident.recipient_phone, *(incident.escalation_phones or [])]:
            if not phone.startswith("+"):
                raise ValueError("all phone numbers must use E.164 format")
        return incident


def build_call_task(i: Incident) -> str:
    return (
        f"You are ShiftBridge, an automated operational handover assistant. Call {i.recipient_phone}. "
        "At the start of the call, clearly identify yourself as an automated ShiftBridge assistant. "
        f"Report a {i.severity.upper()} issue at site {i.site}, line {i.line}: {i.issue}. "
        f"Action already taken: {i.action_taken}. Required next action: {i.next_action}. Deadline: {i.deadline}. "
        "Ask the recipient to briefly restate the unresolved issue or next action in their own words so the handover "
        "has transcript-backed evidence of understanding. Then ask whether they explicitly accept ownership and, if "
        "they do, capture the exact words showing acceptance plus their ETA. If they decline, capture the blocker. "
        "Do not invent facts, quotes, or commitments. Do not claim the incident is resolved unless the called person "
        "explicitly accepts ownership. If the person cannot be reached, does not demonstrate understanding, does not "
        "explicitly accept ownership, or the transcript does not contain supporting words, mark escalation_required=true."
    )


RESULT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "reached_person",
        "understood_issue",
        "acknowledgement_quote",
        "ownership",
        "ownership_quote",
        "eta_or_blocker",
        "escalation_required",
    ],
    "properties": {
        "reached_person": {
            "type": "string",
            "enum": ["yes", "no", "unknown"],
            "description": "Whether a responsible human was actually reached on the call.",
        },
        "understood_issue": {
            "type": "string",
            "enum": ["yes", "no", "unknown"],
            "description": "Whether the called person explicitly demonstrated understanding of the incident.",
        },
        "acknowledgement_quote": {
            "type": "string",
            "description": "Exact short words spoken by the recipient that demonstrate understanding; empty if unsupported.",
        },
        "ownership": {
            "type": "string",
            "enum": ["accepted", "declined", "unknown"],
            "description": "Whether the called person explicitly accepted responsibility for the next action.",
        },
        "ownership_quote": {
            "type": "string",
            "description": "Exact short words spoken by the recipient that support accepted ownership; empty if unsupported.",
        },
        "eta_or_blocker": {
            "type": "string",
            "description": "The person's stated ETA, or the blocker preventing ownership/completion.",
        },
        "escalation_required": {
            "type": "boolean",
            "description": "True when another human must be called because the handoff is not safely closed.",
        },
    },
}


def _read_call_field(call: Any, name: str, default: Any = None) -> Any:
    """Support CALL-E SDK responses represented as either mappings or objects."""
    if isinstance(call, dict):
        return call.get(name, default)
    return getattr(call, name, default)


def _idempotency_key(i: Incident) -> str:
    """Create a stable key so retried host workflows do not place duplicate real calls."""
    material = "|".join(
        [
            i.site,
            i.line,
            i.severity.upper(),
            i.issue,
            i.next_action,
            i.deadline,
            i.recipient_phone,
        ]
    )
    digest = hashlib.sha256(material.encode("utf-8")).hexdigest()[:24]
    return f"shiftbridge-{digest}"


def _call_once(client: CalleClient, i: Incident) -> dict[str, Any]:
    call = client.calls.create_and_wait(
        task=build_call_task(i),
        recipient={"phone": i.recipient_phone},
        result_schema=RESULT_SCHEMA,
        idempotency_key=_idempotency_key(i),
    )
    return {
        "phone": i.recipient_phone,
        "status": _read_call_field(call, "status"),
        "task_completed": _read_call_field(call, "task_completed"),
        "completion_confidence": _read_call_field(call, "completion_confidence"),
        "structured_result": _read_call_field(call, "structured_result") or {},
        "evidence": _read_call_field(call, "evidence"),
    }


def _has_quote(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _needs_escalation(result: dict[str, Any]) -> bool:
    structured = result.get("structured_result") or {}
    if structured.get("escalation_required") is True:
        return True
    return not (
        structured.get("reached_person") == "yes"
        and structured.get("understood_issue") == "yes"
        and _has_quote(structured.get("acknowledgement_quote"))
        and structured.get("ownership") == "accepted"
        and _has_quote(structured.get("ownership_quote"))
    )


def _handover_disposition(result: dict[str, Any], *, chain_exhausted: bool = False) -> str:
    """Map conversation evidence to a deterministic host-workflow state."""
    structured = result.get("structured_result") or {}
    if (
        structured.get("reached_person") == "yes"
        and structured.get("understood_issue") == "yes"
        and _has_quote(structured.get("acknowledgement_quote"))
        and structured.get("ownership") == "accepted"
        and _has_quote(structured.get("ownership_quote"))
        and structured.get("escalation_required") is not True
    ):
        return "accepted"
    if chain_exhausted:
        return "needs_supervisor"
    if structured.get("reached_person") == "no":
        return "unreached"
    return "blocked"


def run_incident(i: Incident) -> dict[str, Any]:
    api_key = os.environ.get("CALLE_API_KEY")
    if not api_key:
        raise RuntimeError("CALLE_API_KEY is not set")
    client = CalleClient(api_key=api_key)
    attempts: list[dict[str, Any]] = []
    phones = [i.recipient_phone, *(i.escalation_phones or [])]

    for phone in phones:
        attempt = _call_once(client, replace(i, recipient_phone=phone, escalation_phones=[]))
        attempts.append(attempt)
        if not _needs_escalation(attempt):
            break

    final = attempts[-1]
    exhausted = _needs_escalation(final) and len(attempts) == len(phones)
    disposition = _handover_disposition(final, chain_exhausted=exhausted)
    return {
        "incident": asdict(i),
        "attempts": attempts,
        "handoff_closed": disposition == "accepted",
        "handover_disposition": disposition,
        "escalation_chain_exhausted": exhausted,
        "final_owner_phone": final["phone"] if disposition == "accepted" else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify a shift handover by phone")
    parser.add_argument("incident", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    incident = Incident.from_dict(json.loads(args.incident.read_text(encoding="utf-8")))
    if args.dry_run:
        phones = [incident.recipient_phone, *(incident.escalation_phones or [])]
        print(
            json.dumps(
                {
                    "incident": asdict(incident),
                    "planned_calls": [
                        build_call_task(replace(incident, recipient_phone=phone, escalation_phones=[]))
                        for phone in phones
                    ],
                    "result_schema": RESULT_SCHEMA,
                },
                indent=2,
            )
        )
        return
    print(json.dumps(run_incident(incident), indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
