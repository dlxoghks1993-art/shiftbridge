# ShiftBridge — AssemblyAI Voice Agent Track

## Goal

Extend the existing ShiftBridge handover-assurance workflow into a voice-first operational escalation agent for the AssemblyAI Voice Agent Hackathon without weakening the CALL-E submission.

## Product thesis

A notification proves that a message was sent. ShiftBridge aims to prove that operational responsibility actually crossed a shift boundary: the incoming owner heard the unresolved condition, restated it, accepted or declined ownership, and surfaced an ETA or blocker.

For the AssemblyAI track, live speech is the primary interface. A supervisor can speak a handover instead of filling a form. The system transcribes the report, extracts a bounded handover packet, asks the speaker to confirm the extracted facts, and then drives the existing acknowledgement/ownership workflow.

## AssemblyAI-specific flow

1. Capture a spoken handover report.
2. Stream/transcribe it with AssemblyAI.
3. Extract only explicitly stated fields: site, line/asset, severity, unresolved issue, actions already taken, required next action, deadline, incoming owner.
4. Read the structured packet back for human confirmation before any outbound escalation.
5. Start the existing ShiftBridge phone handover.
6. Capture recipient read-back, ownership decision, ETA/blocker and evidence quotes.
7. Return `accepted`, `blocked`, `unreached`, or `needs_supervisor`.

## Demo scenario

Night shift on Packaging Line 2 reports a temperature excursion. The operator stopped the line and isolated the affected batch, but the investigation cannot finish before shift change. The outgoing operator speaks the handover. ShiftBridge transcribes and structures it, asks for confirmation, then calls the incoming supervisor. The supervisor must restate the unresolved condition and explicitly accept ownership. A blocker or failed contact becomes a supervisor escalation instead of a false success.

## Safety constraints

- Never invent incident facts or missing fields.
- Never infer that equipment is safe to restart.
- Never treat transcript confidence as operational truth.
- Require human confirmation of the extracted handover packet before outbound action.
- Require transcript-backed acknowledgement and ownership evidence before `accepted`.
- Route ambiguity, refusal, or unreachable recipients to a human supervisor.

## Judging narrative

**Problem:** shift handovers fail when context is written down but responsibility is not actually transferred.

**Why voice:** operational staff can report hands-free and the recipient's live read-back provides evidence that a real person understood the handover.

**Why AssemblyAI:** transcription is not decorative; it converts spoken operational context into the structured contract that drives the workflow and provides auditable evidence for downstream disposition.

**Differentiator:** this is not a generic voice assistant. It is a bounded state-transition agent for high-friction operational handovers with explicit acceptance criteria and fail-closed behavior.

## Implementation checklist

- [ ] Add streaming or file transcription adapter using AssemblyAI.
- [ ] Add transcript-to-handover extraction schema.
- [ ] Add explicit human confirmation gate.
- [ ] Reuse existing disposition/evidence validator.
- [ ] Add demo audio fixture and expected structured packet.
- [ ] Add deterministic dry-run mode for judges.
- [ ] Record a 60–90 second demo showing spoken report -> structured packet -> recipient acceptance/blocker -> final disposition.

## Submission copy draft

**ShiftBridge: Voice-Proven Shift Handover**

ShiftBridge turns a spoken shift handover into an auditable transfer of operational responsibility. An outgoing worker reports unfinished work by voice. AssemblyAI transcribes the report, ShiftBridge structures only the facts that were actually stated, and the worker confirms the packet before escalation. The incoming owner is then contacted and must read back the unresolved condition, explicitly accept ownership, and provide an ETA or blocker. ShiftBridge fails closed: without transcript-backed understanding and ownership evidence, the handover is not marked complete.

The manufacturing demo uses a temperature excursion on a packaging line, but the same handover contract applies to facilities, warehouses, field service and other 24/7 operations where a sent ticket is not proof that responsibility actually changed hands.
