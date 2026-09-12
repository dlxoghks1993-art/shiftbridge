# ShiftBridge — 2 minute demo script

This script is designed to stay safely below the CALL-E hackathon's 3-minute video limit.

## 0:00–0:15 — The problem

On screen: the incident JSON for a P1 temperature excursion on Packaging Line 2.

Voiceover:

> A shift log can say an incident was handed over, but it cannot prove the next responsible person actually received it, understood it, and accepted ownership. ShiftBridge closes that gap with a real phone call.

## 0:15–0:35 — Launch the escalation

On screen: run the app with the supplied incident payload.

Voiceover:

> ShiftBridge takes only structured incident facts: site, severity, what happened, actions already taken, the required next action, the deadline, and the authorized recipient. It then asks CALL-E to place the escalation call.

## 0:35–1:15 — Show the real call

Record the recipient phone receiving the call alongside the terminal/app output.

Suggested recipient answers for the success path:

- Confirms they are the incoming supervisor.
- Restates the temperature excursion in their own words.
- Accepts ownership.
- Gives a concrete ETA, e.g. "I can be at Line 2 in 15 minutes."

Voiceover after the call:

> CALL-E is not an ornamental integration here. The phone conversation is the execution layer: it converts an alert into a human acknowledgement and ownership decision.

## 1:15–1:35 — Structured result

On screen: returned result JSON.

Highlight:

- `reached_person = yes`
- `understood_issue = yes`
- `ownership = accepted`
- `eta_or_blocker = 15 minutes`
- `escalation_required = false`

Voiceover:

> The output is machine-readable, so a ticketing system, CMMS, or shift log can act on the result instead of merely recording that a notification was sent.

## 1:35–1:55 — Failure path

Show a second prepared result or live call where the recipient declines ownership or cannot meet the deadline.

Voiceover:

> The stronger case is failure. ShiftBridge never invents a commitment. If the recipient declines, cannot be reached, or reports a blocker, it returns `escalation_required=true` so the workflow can move to the next authorized human.

## 1:55–2:05 — Close

On screen: project title and simple flow diagram.

Voiceover:

> ShiftBridge turns "message sent" into "responsibility verified." The same pattern applies to manufacturing, facilities, logistics, field service, and overnight IT operations.

## Recording checklist

- Show an actual CALL-E-powered call, not only mocked output.
- Keep the final public video under 3 minutes.
- Avoid copyrighted music and third-party brand footage.
- Do not display API keys, private phone numbers, or other credentials.
- Use only a phone number whose owner has agreed to receive the demo call.
- Make the returned structured fields legible on screen.
