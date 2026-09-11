# ShiftBridge Call Escalator

ShiftBridge turns a shift-handover incident into a real outbound escalation call, then returns machine-readable evidence about acknowledgement, ownership, blockers, and whether a supervisor must be involved.

## Why this exists

Critical shift handovers often fail at the last mile: a note is written, but nobody proves that the next responsible person actually received it, understood it, and accepted ownership. ShiftBridge closes that gap by using CALL-E as the phone execution layer.

## What the agent does

1. Accepts a structured incident (`site`, `line`, severity, issue, actions already taken, required next action, deadline, recipient phone).
2. Calls the responsible person through CALL-E.
3. Clearly identifies itself as an automated operational handover assistant.
4. Confirms that the person understands the incident.
5. Asks whether they accept ownership and captures an ETA or blocker.
6. Returns structured fields plus CALL-E evidence so downstream systems can decide whether to escalate further.

## Demo scenario

A night shift discovers a temperature excursion on Packaging Line 2. The operator has already stopped the line and isolated the affected batch. The incoming supervisor must acknowledge the event, accept ownership of the investigation, and give an ETA before the restart deadline.

`examples/p1_temperature_excursion.json` contains a ready-to-edit payload for this scenario.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export CALLE_API_KEY="your_free_call_e_key"
python app.py examples/p1_temperature_excursion.json --dry-run
python app.py examples/p1_temperature_excursion.json
```

The API key is read only from the environment and should never be committed.

## Structured result

ShiftBridge requests these fields from CALL-E:

```json
{
  "reached_person": "yes | no | unknown",
  "understood_issue": "yes | no | unknown",
  "ownership": "accepted | declined | unknown",
  "eta_or_blocker": "free-text evidence",
  "escalation_required": true
}
```

## Hackathon positioning

**Core idea:** AI agents usually stop at sending messages. ShiftBridge crosses into the physical world and proves the handoff by speaking to the responsible human.

**CALL-E is essential, not decorative:** the product value is the completed phone escalation and the structured evidence returned from the conversation.

**Useful beyond factories:** the same workflow can handle facilities incidents, logistics delays, field-service escalation, overnight IT operations, and healthcare-adjacent administrative handoffs where a human acknowledgement is required.

## Safety / scope

This prototype does not make safety-critical decisions on behalf of humans. It relays supplied incident facts, collects acknowledgement and ownership status, and flags when a human supervisor should be involved. It is designed to avoid inventing facts or commitments.
