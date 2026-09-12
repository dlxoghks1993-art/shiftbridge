# CALL-E Devpost submission package

## Project name
ShiftBridge Call Escalator

## Tagline
A CALL-E-powered handover agent that phones the responsible human and returns structured proof of acknowledgement, ownership, ETA, and escalation state.

## Short description
ShiftBridge solves the last-mile failure in operational handovers. Instead of stopping at a ticket, alert, or chat message, it uses CALL-E to place a real phone call to the responsible person, relay only supplied incident facts, confirm understanding, ask them to accept ownership, capture an ETA or blocker, and return a machine-readable escalation result.

The demo uses a P1 manufacturing temperature excursion, but the same pattern applies to facilities, logistics, field service, and overnight IT operations. CALL-E is essential to the product because the core output is not “notification sent”; it is evidence that responsibility was actually transferred to a human or that further escalation is required.

## Inspiration
Critical incidents often cross a shift boundary. Existing tools are good at generating alerts, tickets, and messages, but those artifacts do not prove that the next responsible human received the information, understood it, and accepted responsibility. ShiftBridge was built to close that gap.

## What it does
1. Receives a structured incident and authorized recipient.
2. Uses CALL-E to make the outbound escalation call.
3. Identifies itself as an automated operational handover assistant.
4. Relays only the supplied incident facts.
5. Confirms understanding and asks whether the recipient accepts ownership.
6. Captures an ETA or blocker.
7. Returns structured fields indicating whether another human escalation is required.

## How we built it
The prototype is a small Python application around CALL-E. Incident context is supplied as JSON, converted into a tightly scoped call goal, and sent through the CALL-E execution layer. The application then converts the returned conversation evidence into a deterministic operational result: reached/not reached, understood/not understood, ownership accepted/declined, ETA or blocker, and escalation required/not required.

## Challenges
The main design challenge was preventing a voice agent from becoming the decision-maker in a safety-sensitive workflow. ShiftBridge therefore does not decide whether equipment is safe, invent incident details, or create commitments on behalf of the recipient. Its job is narrower: communicate supplied facts, collect the human response, and flag when another authorized human needs to be involved.

## Accomplishments
- CALL-E is part of the core workflow rather than a cosmetic integration.
- The demo has both a successful handoff and a failure/escalation path.
- The result is structured for downstream automation instead of being only a transcript or summary.
- The architecture can grow into policy-driven escalation trees while keeping humans responsible for operational decisions.

## What we learned
Phone calls are useful when the system needs explicit human acknowledgement, but the valuable software layer is the state transition around the call: who was reached, what they understood, whether they accepted ownership, and what happens next. Treating the call as an auditable workflow step makes voice agents more useful than generic outbound calling.

## What's next
A production version would support configurable escalation trees, retry windows, shift rosters, write-back to CMMS/ticketing systems, audit timelines, and organization-specific handover policies. If the first contact cannot take ownership, ShiftBridge would call the next authorized person while preserving the full escalation history.

## Required submission checklist
- [ ] Join the CALL-E hackathon on Devpost.
- [ ] Create/log in to a CALL-E account and retain the account email.
- [ ] Run at least one real CALL-E demo call successfully.
- [ ] Record a public YouTube or Vimeo demo under 3 minutes.
- [ ] Ensure the video visibly shows the project functioning.
- [ ] Provide the email associated with the CALL-E account.
- [ ] Complete every required Devpost submission field.
- [ ] Submit before the official deadline.

## Final QA before submission
- No API key, private number, or credential visible in video/screenshots.
- No copyrighted music or unlicensed third-party footage.
- English narration/text, or English translation/subtitles if another language is used.
- Repository is publicly accessible if linked.
- Demo behavior matches the claims in the written description.
- Failure path is represented honestly; no fabricated CALL-E result is presented as a real call.
