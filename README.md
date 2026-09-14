# ShiftBridge Handover Assurance

ShiftBridge turns a **shift-to-shift operational handover** into a real CALL-E phone conversation and returns structured evidence about what the incoming owner actually heard, accepted, and still needs to resolve.

## Why this exists

Factories, facilities, warehouses, field-service teams, and other 24/7 operations routinely transfer unfinished work across shift boundaries. A logbook entry, ticket, or chat message proves that information was written down — not that the incoming owner understood the exact unresolved condition, accepted the next action, or surfaced a blocker before the outgoing shift disappears.

ShiftBridge treats the phone call as a **handover checkpoint**, not a generic incident page. It is designed around the outgoing-to-incoming shift transition: unresolved work, actions already taken, the required next action, a deadline, and explicit read-back/ownership evidence.

## What the agent does

1. Accepts a structured handover packet (`site`, `line`, severity, unresolved issue, actions already taken, required next action, deadline, incoming owner phone).
2. Builds a bounded call task from only those supplied facts.
3. Calls the incoming owner through CALL-E.
4. Clearly identifies itself as an automated operational handover assistant.
5. Asks the recipient to restate the unresolved condition or next action in their own words.
6. Asks whether they explicitly accept ownership and captures their ETA or blocker.
7. Requires short transcript-backed acknowledgement and ownership quotes before the host can mark a handover accepted.
8. Returns structured fields so the host workflow can mark the handover `accepted`, `blocked`, `unreached`, or `needs_supervisor`.

## Demo scenario

A night shift finds a temperature excursion on Packaging Line 2. The operator stops the line and isolates the affected batch, but the investigation cannot finish before shift change. ShiftBridge phones the incoming supervisor with the exact known facts, asks for a read-back of the unresolved condition, asks for explicit ownership, and records either evidence-backed acceptance/ETA or a blocker requiring supervisor follow-up.

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
  "acknowledgement_quote": "exact short read-back from the recipient",
  "ownership": "accepted | declined | unknown",
  "ownership_quote": "exact short words supporting accepted ownership",
  "eta_or_blocker": "free-text evidence",
  "escalation_required": true
}
```

The host fails closed: an `accepted` label alone is insufficient. Both understanding and ownership must be supported by non-empty recipient quotes before the handover is considered closed. This keeps downstream automation from treating an unsupported model classification as proof that responsibility actually crossed the shift boundary.

## How this differs from a normal incident-escalation pager

The CALL-E community already has an `incident-escalation-call` pattern for waking an on-call engineer and walking an escalation ladder. ShiftBridge deliberately targets a different operational moment:

- **ShiftBridge starts with an outgoing shift's unfinished work**, not a monitoring page.
- The primary recipient is the **known incoming owner**, not a dynamically resolved on-call ladder.
- The payload includes **actions already taken + required next action + deadline**, so the call is a continuity check rather than just an alert.
- The recipient provides a **read-back plus explicit ownership evidence**, making the transfer auditable instead of relying only on a status label.
- The useful output is a **handover disposition** (`accepted`, `blocked`, `unreached`, `needs_supervisor`) that a shift log, CMMS, or production workflow can store.
- A future escalation tree is secondary; the core product is proving that responsibility crossed the shift boundary with the right context intact.

## Hackathon positioning

**Specific phone-work problem:** unfinished operational work crosses a shift boundary, but the outgoing team cannot tell whether the next owner actually absorbed the context before they leave.

**Why a phone call is necessary:** the workflow needs a live read-back, explicit acknowledgement, and an opportunity for the incoming owner to surface a blocker immediately. A sent notification cannot provide that state transition.

**CALL-E is essential, not decorative:** the core artifact is the structured result of a real conversation. Without CALL-E, ShiftBridge collapses back into another ticket or notification.

**Reusable direction:** manufacturing shift changes are the demo, but the same handover contract applies to facilities rounds, warehouse exceptions, field-service continuity, overnight operations, and other staffed 24/7 environments.

## Safety / scope

This prototype does not decide whether equipment is safe, restart machinery, approve maintenance, or make emergency decisions. It relays supplied handover facts, collects acknowledgement/ownership evidence, and flags when an authorized human needs to take the next step. It is designed to avoid inventing incident facts, transcript quotes, or commitments.
