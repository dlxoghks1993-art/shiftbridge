# ShiftBridge live submission checklist

Use this only after a CALL-E account/API key is available. The goal is to collect proof that the project actually calls CALL-E at runtime and to avoid spending scarce free calls on avoidable mistakes.

## 0. Region check before any live demo

CALL-E's current official supported-region table does **not** include South Korea (`+82`). Do not assume a Korean mobile number can be used for the live demo.

For a real outbound demo, use only a phone number that the entrant controls or has explicit permission to call **and** whose country code is currently supported by CALL-E. Re-check the provider's supported-region table immediately before testing because provider coverage can change.

If the only authorized number available is `+82`, do not fabricate a successful call or edit screenshots/transcripts to imply one happened. Keep the application functional for supported numbers, show the dry-run honestly, and record the provider limitation as reproducible product feedback. A real supported-region call remains the strongest evidence for the hackathon's technical-implementation criterion.

## 1. Preflight without placing a call

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m unittest -v
python app.py examples/p1_temperature_excursion.json --dry-run
```

Confirm the dry-run output contains:

- the correct recipient phone in E.164 format
- the exact site / line / issue / next action / deadline
- the structured result schema
- no API key or other secret

## 2. Put a safe demo number in the example payload

Edit `examples/p1_temperature_excursion.json` so `recipient_phone` is a number the entrant controls or has permission to call. Remove `escalation_phones` for the first live test so a failed demo cannot place extra calls.

Never commit a real private phone number.

## 3. Run one live CALL-E call

```bash
export CALLE_API_KEY="..."   # PowerShell: $env:CALLE_API_KEY="..."
python app.py examples/p1_temperature_excursion.json
```

Expected output includes:

- `attempts[0].status`
- `attempts[0].structured_result`
- `handover_disposition`
- `handoff_closed`

A successful demo should show the called human explicitly acknowledging the issue and accepting ownership, producing `handover_disposition: "accepted"`.

## 4. Capture evidence for the demo video

Record these in one continuous sequence where possible:

1. repository / README
2. the incident JSON with any private number obscured
3. terminal command that launches ShiftBridge
4. the real incoming CALL-E phone call
5. the spoken acknowledgement / ownership response
6. the terminal's structured result and final disposition

Do not expose the API key, private phone number, or unrelated personal information in the recording.

## 5. Failure-path proof

If free-call budget permits, run a second controlled scenario where the recipient declines ownership or states a blocker. The useful proof is that ShiftBridge does **not** mark the handover accepted and instead returns `blocked`, `unreached`, or `needs_supervisor`.

This demonstrates that the product is not just a phone-call wrapper: the conversation changes the host workflow state.

## 6. Community contribution

Prepare the required contribution to `CALLE-AI/awesome-phone-call-agents` using the repository's current contribution format. Link back to this public repository and describe ShiftBridge as a shift-to-shift handover assurance agent, not a generic incident pager.

Before opening the PR, verify the upstream repository's latest README / contribution instructions so the entry matches its current schema.

## 7. Devpost submission package

Use:

- `DEVPOST_SUBMISSION.md` for the long-form submission
- `DEMO_SCRIPT.md` for the sub-3-minute demo narration
- this repository URL as the public source-code link
- the public demo-video URL after upload
- the CALL-E account email required by the submission form

Final check before submitting:

- CALL-E is actually called at runtime when an authorized supported-region recipient is available
- any unsupported-region limitation is described accurately rather than presented as a successful call
- project installs and runs as shown
- public repository is accessible
- demo video is public and under the event time limit
- no secrets or private phone numbers are committed or visible
- required upstream PR is submitted and linked
- all mandatory Devpost fields are complete

## 8. Feedback-prize notes

During live testing, record concrete CALL-E feedback separately: SDK/API friction, documentation gaps, result-schema behavior, call latency, dashboard UX, or integration ideas. Actionable reproducible observations are more useful than general praise and can be reused in the hackathon feedback submission.

For a South Korea entrant, the absence of `+82` in the supported-region table is itself a concrete, reproducible product-coverage limitation worth documenting accurately in feedback. The feedback submission remains separate from the main project submission and should not claim that an unsupported live call succeeded.
