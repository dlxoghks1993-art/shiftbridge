# ShiftBridge — CALL-E Submission Draft

## One-line pitch
ShiftBridge is a phone-native shift-handover agent that proves unfinished operational work was actually understood and accepted by the incoming owner before the outgoing shift disappears.

## Problem
Factories, warehouses, facilities, and field-service teams transfer unresolved work across shift boundaries every day. Tickets and chat messages prove information was sent, but they do not prove the next owner understood the unresolved condition, accepted responsibility, or surfaced a blocker while the outgoing operator was still available.

## Why CALL-E
This workflow needs a live conversation. ShiftBridge uses CALL-E to reach the known incoming owner, disclose that it is an automated handover assistant, relay only the supplied incident facts, request a read-back, obtain explicit ownership, and capture an ETA or blocker. The useful artifact is not merely a notification: it is transcript-backed evidence that responsibility crossed the shift boundary.

## Demo
**Scenario:** Packaging Line 2 has a temperature excursion shortly before shift change. The outgoing operator has stopped the line and isolated the affected batch, but investigation is unfinished.

1. The host sends ShiftBridge a structured handover packet with site, line, severity, unresolved issue, actions already taken, required next action, deadline, and incoming-owner phone number.
2. ShiftBridge calls the incoming supervisor through CALL-E.
3. The agent identifies itself as automated and gives the bounded handover facts.
4. It asks the supervisor to restate the issue or next action in their own words.
5. It asks for explicit ownership and an ETA, or records the blocker.
6. The host accepts the handover only when the structured result contains both understanding and ownership backed by non-empty recipient quotes.
7. If the recipient is unreachable, does not demonstrate understanding, or declines ownership, ShiftBridge proceeds through the configured escalation chain and ultimately returns `needs_supervisor` if nobody safely accepts the handover.

## What makes it different
This is not an incident pager. Incident pagers primarily alert or locate an on-call responder. ShiftBridge begins at a specific operational transition: an outgoing shift has unfinished work and a known incoming owner. It carries forward actions already taken, the required next action, and the deadline, then verifies continuity with read-back plus explicit ownership evidence.

## Safety and reliability
- The agent may relay only facts supplied in the handover packet.
- It may not decide equipment safety, restart machinery, approve maintenance, or make emergency decisions.
- It must disclose that it is automated.
- A model-generated `accepted` label is insufficient by itself; acknowledgement and ownership require transcript-backed quotes.
- Failed or ambiguous handovers fail closed into escalation rather than being marked complete.
- Stable idempotency keys reduce duplicate real calls when host workflows retry.

## Reusability
Manufacturing is the demo, but the same handover contract applies to facilities rounds, warehouse exceptions, field-service continuity, overnight operations, security operations, and other staffed 24/7 workflows.

## Suggested 90-second demo recording
**0–15s:** Show the JSON handover packet and explain the gap: “a ticket proves this was written, not that the next shift accepted it.”

**15–55s:** Run ShiftBridge and show the CALL-E conversation: automated disclosure → bounded facts → read-back request → explicit ownership → ETA/blocker.

**55–75s:** Show the structured result and the host-side `accepted` disposition only when transcript-backed acknowledgement and ownership are present.

**75–90s:** Show the failure path: unreachable/declined/unsupported response triggers escalation and eventually `needs_supervisor` instead of a false success.

## Submission description
ShiftBridge turns operational shift change into a verifiable phone handover. When unfinished work must cross from an outgoing shift to an incoming owner, it uses CALL-E to relay the exact supplied context, request a read-back, capture explicit ownership and ETA/blocker, and return structured evidence to the host workflow. The handover fails closed: without transcript-backed understanding and ownership, ShiftBridge escalates rather than pretending responsibility transferred. The result is a reusable phone-native continuity layer for factories, facilities, warehouses, field service, and other 24/7 operations.