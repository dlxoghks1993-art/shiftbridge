"""ShiftBridge Professional Agent entrypoint for the Agents for Humans hackathon.

This keeps CALL-E as the phone execution layer while Strands Agents decides when a
handover packet is complete enough to place a call and how to interpret the host-side
workflow state. It is intentionally conservative: unsafe or incomplete packets are
rejected before any phone call is attempted.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from strands import Agent, tool

from app import Incident, build_call_task, run_incident


@tool
def inspect_handover_packet(packet_json: str) -> dict[str, Any]:
    """Validate a proposed shift handover before any external action.

    Args:
        packet_json: JSON string containing the ShiftBridge incident packet.
    """
    try:
        raw = json.loads(packet_json)
        incident = Incident.from_dict(raw)
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        return {"valid": False, "error": str(exc)}

    required_text = {
        "site": incident.site,
        "line": incident.line,
        "issue": incident.issue,
        "action_taken": incident.action_taken,
        "next_action": incident.next_action,
        "deadline": incident.deadline,
    }
    empty = [name for name, value in required_text.items() if not value.strip()]
    if empty:
        return {"valid": False, "error": f"Empty fields: {', '.join(empty)}"}

    return {
        "valid": True,
        "severity": incident.severity.upper(),
        "site": incident.site,
        "line": incident.line,
        "recipient_phone": incident.recipient_phone,
        "escalation_count": len(incident.escalation_phones or []),
        "call_preview": build_call_task(incident),
    }


@tool
def execute_verified_handover(packet_json: str) -> dict[str, Any]:
    """Execute a validated ShiftBridge handover through CALL-E.

    Use this only after inspect_handover_packet returned valid=true. The CALL-E API
    key must be supplied through CALLE_API_KEY. The function uses ShiftBridge's
    deterministic evidence gates and idempotency protection.

    Args:
        packet_json: JSON string containing the ShiftBridge incident packet.
    """
    incident = Incident.from_dict(json.loads(packet_json))
    return run_incident(incident)


SYSTEM_PROMPT = """You are ShiftBridge, a professional operations handover agent.
Your job is to prevent unfinished work from disappearing at shift change.

Rules:
1. Always call inspect_handover_packet before considering any external action.
2. Never invent missing incident facts, phone numbers, deadlines, quotes, or approvals.
3. Do not decide whether machinery is safe, authorize a restart, or make emergency decisions.
4. If validation fails, explain exactly what an authorized human must supply and stop.
5. Only use execute_verified_handover when the user explicitly asks to execute the handover.
6. Treat CALL-E's transcript-backed acknowledgement and ownership evidence as authoritative;
   do not upgrade an unsupported result to accepted.
7. If the handover is blocked, unreached, or needs_supervisor, surface that decision to a human.
"""


def build_agent() -> Agent:
    return Agent(
        system_prompt=SYSTEM_PROMPT,
        tools=[inspect_handover_packet, execute_verified_handover],
        trace_attributes={"service": "shiftbridge", "workflow": "shift-handover"},
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run ShiftBridge as a Strands Agent")
    parser.add_argument("incident", type=Path)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Allow the agent to place the CALL-E handover call after validation.",
    )
    args = parser.parse_args()

    packet_json = args.incident.read_text(encoding="utf-8")
    action = (
        "Validate this handover packet and, if valid, execute the phone handover."
        if args.execute
        else "Validate this handover packet. Do not place a phone call."
    )
    prompt = f"{action}\n\nHANDOVER_PACKET_JSON:\n{packet_json}"
    result = build_agent()(prompt)
    print(result)


if __name__ == "__main__":
    main()
