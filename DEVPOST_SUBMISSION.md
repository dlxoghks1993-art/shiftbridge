# CALL-E Devpost submission package

## Project name
ShiftBridge Handover Assurance

## Tagline
A CALL-E-powered shift handover checkpoint that phones the incoming owner and returns transcript-backed proof that unfinished operational work was understood, accepted, blocked, or needs supervisor follow-up.

## Short description
ShiftBridge solves a specific failure in 24/7 operations: critical unfinished work crosses a shift boundary, but the outgoing team cannot prove that the incoming owner actually absorbed the context before they leave.

Instead of treating a ticket, logbook entry, or chat message as a completed handover, ShiftBridge uses CALL-E to place a real phone call to the known incoming owner. It relays only the supplied facts, asks the recipient to restate the unresolved issue or next action in their own words, asks whether they explicitly accept ownership, captures an ETA or blocker, and returns a machine-readable handover disposition backed by short recipient quotes.

The demo uses a manufacturing temperature excursion. The same pattern can be reused for facilities rounds, warehouse exceptions, field service, overnight operations, and other shift-based environments where continuity matters.

## Inspiration
Shift handovers are an operational blind spot. Systems are very good at recording that information was sent; they are much worse at proving that responsibility crossed the boundary with the context intact. The outgoing shift may leave after writing a note, while the incoming owner discovers much later that an unresolved condition, deadline, or prior action was misunderstood.

ShiftBridge was built around a simple question: **did the unfinished work actually make it into the next human's head, with an owner and a next step?**

## What it does
1. Receives a structured handover packet and authorized incoming owner.
2. Builds a bounded phone-call task from the unresolved issue, actions already taken, required next action, and deadline.
3. Uses CALL-E to call the incoming owner.
4. Identifies itself as an automated operational handover assistant.
5. Asks the recipient to restate the unresolved condition or next action in their own words.
6. Asks whether they explicitly accept ownership and captures an ETA or blocker.
7. Requires transcript-backed acknowledgement and ownership quotes before the workflow can mark the handover accepted.
8. Returns a structured disposition such as `accepted`, `blocked`, `unreached`, or `needs_supervisor` for downstream shift logs, CMMS, or production workflows.

## How we built it
The prototype is a small Python application around CALL-E. Handover context is supplied as JSON, converted into a tightly scoped call goal, and sent through the CALL-E execution layer. The application interprets the returned conversation evidence into operational fields: reached/not reached, understood/not understood, acknowledgement quote, ownership accepted/declined, ownership quote, ETA or blocker, and escalation required/not required.

The host workflow is intentionally fail-closed. Even if a model labels the call `accepted`, ShiftBridge will not close the handover unless the result also contains recipient words supporting both understanding and ownership. A dry-run path makes the exact call task inspectable before any real-world side effect occurs. API credentials remain in environment variables rather than source.

## Why this is not just another incident pager
The CALL-E community already includes an `incident-escalation-call` workflow for waking an on-call engineer and walking an escalation ladder. ShiftBridge targets a different problem and deliberately avoids duplicating that contribution.

- It starts with an **outgoing shift's unfinished work**, not a monitoring alert.
- It calls the **known incoming owner**, not an on-call rotation.
- It carries **actions already taken, required next action, and deadline** so context survives the shift boundary.
- It asks for a **read-back and explicit ownership evidence**, not merely acknowledgement of an alert.
- Its primary result is a **handover disposition** suitable for a shift log or operations system.
- Supervisor escalation is a failure path, not the product's main loop.

## Challenges
The key design challenge was using a voice agent without turning it into the operational decision-maker. ShiftBridge does not decide whether equipment is safe, restart machinery, invent incident details, or create commitments on behalf of the recipient. Its job is narrower: communicate supplied facts, collect the human response, preserve the recipient's own words as evidence, and flag when another authorized human needs to be involved.

A second challenge was differentiating a shift-handover product from generic incident escalation. The design therefore centers on continuity-of-work fields, a known incoming owner, and evidence of successful knowledge transfer instead of an on-call ladder.

## Accomplishments
- CALL-E is part of the core state transition rather than a cosmetic integration.
- The workflow focuses on a specific real-world phone-work problem: shift-to-shift continuity.
- A handover cannot close from a bare classifier label; acceptance requires transcript-backed understanding and ownership evidence.
- The demo includes both a successful handover and a blocker/escalation path.
- The result is structured for downstream automation instead of being only a transcript or summary.
- The application has a preview/dry-run path so the operator can inspect the call before a real phone call is placed.
- Stable idempotency keys reduce the risk of duplicate real calls when a host workflow retries.

## What we learned
The valuable software layer around a phone call is not merely the transcript. In shift work, the important state transition is whether the incoming person understood the unfinished work, accepted the next action, and surfaced a blocker while the outgoing team could still respond. Requiring the recipient's own words as evidence makes that state transition more auditable and keeps downstream automation from over-trusting an unsupported model classification.

## What's next
A production version would add shift-roster integration, CMMS/ticket write-back, deadline-aware supervisor escalation, audit timelines, and organization-specific handover policies. The escalation layer would remain downstream of the core handover checkpoint rather than replacing it.

## Required submission checklist
- [ ] Join the CALL-E hackathon on Devpost.
- [ ] Create/log in to a CALL-E account and retain the account email.
- [ ] Run at least one real CALL-E demo call successfully.
- [ ] Prepare the contribution under the correct area of `CALLE-AI/awesome-phone-call-agents` and open the required pull request.
- [ ] Put that pull-request URL in the Devpost submission.
- [ ] Record a public YouTube or Vimeo demo under three minutes.
- [ ] Ensure the video visibly shows CALL-E being called at runtime and the returned structured result.
- [ ] Show the transcript-backed acknowledgement/ownership evidence or an honest failed-closed path.
- [ ] Provide the email associated with the CALL-E account.
- [ ] Complete every required Devpost submission field.
- [ ] Submit before September 14, 2026 at 11:45 PM SGT.

## Final QA before submission
- No API key, private number, or credential visible in video/screenshots.
- No copyrighted music or unlicensed third-party footage.
- English narration/text, or English translation/subtitles if another language is used.
- Repository and required submission PR are publicly accessible.
- Demo behavior matches the written claims.
- CALL-E is actually imported/called at runtime; the integration is not only referenced in text.
- Failure path is represented honestly; no fabricated CALL-E result is presented as a real call.
