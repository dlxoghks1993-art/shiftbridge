# ShiftBridge — Agents for Humans demo script (target: 3:30–4:15)

## 0:00–0:25 — Hook / problem
“Shift changes are one of the easiest places for unfinished operational work to disappear. A ticket proves someone wrote something down. It does not prove the incoming owner understood the unresolved condition, accepted the next action, or surfaced a blocker before the outgoing shift leaves.”

On screen: README title + the example packet in `examples/p1_temperature_excursion.json`.

## 0:25–0:55 — What ShiftBridge is
“ShiftBridge is a Professional Agent built with the Strands Agents SDK. It validates a structured handover packet, refuses to invent missing facts, and—only when execution is explicitly requested—uses CALL-E to conduct a bounded phone handover with the incoming owner.”

On screen: `strands_agent.py`, highlighting `Agent`, `@tool`, `inspect_handover_packet`, and `execute_verified_handover`.

## 0:55–1:35 — Safe validation first
Run:

```bash
python strands_agent.py examples/p1_temperature_excursion.json
```

Explain: “The agent inspects the packet before any side effect. Missing site, line, issue, next action, deadline, or recipient information stops the workflow. The model is not allowed to invent operational facts.”

If a live model provider is not configured, show the code path and run the host dry-run instead:

```bash
python app.py examples/p1_temperature_excursion.json --dry-run
```

## 1:35–2:20 — Why phone is useful
Show the call task generated from the example.

“The call is not a generic alert. The recipient is asked to restate the unresolved condition or next action, explicitly accept or decline ownership, and provide an ETA or blocker. That makes the transfer auditable instead of treating ‘message sent’ as ‘responsibility transferred.’”

## 2:20–3:05 — Evidence gate
Show the structured result schema in README or the relevant host-side code in `app.py`.

“ShiftBridge fails closed. An `accepted` label alone is not enough. The host requires transcript-backed acknowledgement and ownership evidence before it closes the handover. Otherwise the result is `blocked`, `unreached`, or `needs_supervisor`.”

If a supported CALL-E number and API key are available, run:

```bash
python strands_agent.py examples/p1_temperature_excursion.json --execute
```

If not, state the limitation clearly and demonstrate the deterministic dry-run/test path rather than claiming a live call occurred.

## 3:05–3:40 — Human boundary
“ShiftBridge does not decide whether machinery is safe, authorize a restart, or make emergency decisions. It automates repetitive continuity work and surfaces a person only when a real decision, blocker, or failed transfer remains.”

On screen: system prompt safety rules and final disposition.

## 3:40–4:05 — Close
“ShiftBridge turns shift handover from a passive record into an evidence-backed transfer of responsibility. Manufacturing is the demo, but the same contract applies to facilities, warehouses, field service, and any 24/7 operation where unfinished work crosses a shift boundary.”

Final screen: repository URL and architecture diagram from `AGENTS_FOR_HUMANS_SUBMISSION.md`.

## Recording checklist
- Keep total video under 5 minutes.
- Show a working execution path; do not fabricate a CALL-E success if the recipient country/number is unsupported.
- Cover problem, target user, why it matters, and how Strands Agents is used.
- Make the public repository URL visible.
- Mention MIT license.
- Use the architecture diagram in the submission draft.
