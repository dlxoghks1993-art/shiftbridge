---
name: shift-handover-assurance
description: Verify that unfinished operational work really transfers across a shift boundary. Uses CALL-E to call the known incoming owner, collect a spoken read-back, explicit ownership and ETA/blocker evidence, and return a deterministic handover disposition. Use when a shift log or ticket proves that information was written down but not that the next human actually accepted responsibility.
license: MIT
---

# Shift Handover Assurance

Use this skill when unfinished work must cross a staffed shift boundary and the outgoing team needs evidence that the incoming owner heard the right facts, understood the required next action, and explicitly accepted responsibility.

This is deliberately different from a normal incident pager. The primary recipient is the **known incoming owner**. The call is a continuity checkpoint around supplied handover facts: unresolved condition, actions already taken, required next action, deadline, read-back, ownership and ETA/blocker.

A reference implementation lives in the ShiftBridge repository and uses CALL-E's Python SDK at runtime:

- project: `https://github.com/dlxoghks1993-art/shiftbridge`
- entry point: `app.py`
- dry-run fixture: `examples/p1_temperature_excursion.json`

## When to use

- A factory, facility, warehouse, field-service or other 24/7 operation has unfinished work at shift change.
- The outgoing shift knows exactly who is expected to take over and has an enrolled E.164 number for that person.
- A ticket, logbook or chat message is not enough because the workflow needs a live read-back, explicit ownership and an opportunity to surface a blocker before the outgoing shift leaves.

## When not to use

- The incoming owner is already present in the same conversation and can acknowledge directly.
- The phone number is guessed, scraped, stale, not enrolled for operational calls, or not in E.164 form.
- The request involves emergency dispatch, medical advice, legal advice, financial decisions, machinery restart authorization, or any safety-critical decision that belongs to an authorized human.
- A person has explicitly declined. A decline is not permission to keep retrying that same person.

## Workflow

1. Build a handover packet containing only verified facts supplied by the operator or source system: site, line/asset, severity, unresolved issue, actions already taken, required next action, deadline and the known incoming owner's enrolled phone number.
2. Run the reference app in `--dry-run` first. Review the exact planned call task and structured result schema. Dry-run places no call and needs no credential.
3. Obtain explicit user authorization for the live outbound call and any pre-declared escalation contacts.
4. Run the reference app live with `CALLE_API_KEY` in the environment. The app calls CALL-E through `CalleClient.calls.create_and_wait(...)` and passes the recipient explicitly.
5. The CALL-E task identifies itself as an automated ShiftBridge assistant, states only the supplied handover facts, asks the recipient to restate the unresolved issue or next action, and then asks whether they explicitly accept ownership plus an ETA or blocker.
6. Treat a handover as accepted only when the structured result says a person was reached, understanding was demonstrated, an acknowledgement quote is present, ownership is explicitly accepted, an ownership quote is present, and no escalation is required.
7. Otherwise report `blocked`, `unreached`, or `needs_supervisor`. Do not manufacture a successful handoff from a vague acknowledgement.

## Preview

```bash
git clone https://github.com/dlxoghks1993-art/shiftbridge.git
cd shiftbridge
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py examples/p1_temperature_excursion.json --dry-run
```

The preview path opens no call and does not require `CALLE_API_KEY`.

## Live run

A live run creates an external phone call. Do this only after the user has explicitly asked to place the handover call and has confirmed that the listed recipients are enrolled for this workflow.

```bash
export CALLE_API_KEY="..."  # PowerShell: $env:CALLE_API_KEY="..."
python app.py examples/p1_temperature_excursion.json
```

The reference app sends CALL-E a JSON-schema result contract with these fields:

- `reached_person`: `yes | no | unknown`
- `understood_issue`: `yes | no | unknown`
- `acknowledgement_quote`: short transcript-backed read-back
- `ownership`: `accepted | declined | unknown`
- `ownership_quote`: short transcript-backed ownership evidence
- `eta_or_blocker`: the recipient's stated ETA or blocker
- `escalation_required`: boolean

It also uses a stable idempotency key derived from the handover facts and recipient so a retried host workflow does not intentionally create duplicate calls for the same handover packet.

## How to report the result

- `accepted`: state that the incoming owner explicitly accepted the handover, and report only the minimum operational evidence needed by the workflow.
- `blocked`: state that a person was reached but the handover did not meet the evidence contract. Surface the blocker; do not call it accepted.
- `unreached`: state that the intended recipient was not reached.
- `needs_supervisor`: the declared contact chain is exhausted without an evidence-backed acceptance; hand control to an authorized supervisor.

Mask phone numbers in user-facing summaries. Never print `CALLE_API_KEY` or commit it to a file.

## Rules

- A sent call is not a successful handover. Only transcript-backed understanding plus explicit ownership closes it.
- Never invent incident facts, transcript quotes, owners, ETAs, blockers, phone numbers or escalation contacts.
- Never infer consent to call from a phone number merely existing in a record.
- Never turn the workflow into an undisclosed recurring schedule.
- Do not silently retry an unknown call state; a phone may still be ringing or connected.
- The skill communicates and verifies handover state. It does not authorize equipment restart, emergency response or other safety-critical actions.

## More

- [`references/examples.md`](references/examples.md): worked preview, accepted and blocked outcomes.
- [`references/safety.md`](references/safety.md): consent, recipient enrollment, privacy, duplicate-call and safety boundaries.
