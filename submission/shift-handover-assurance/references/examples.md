# Examples

All phone numbers below are synthetic placeholders. Replace them only with enrolled E.164 contacts that the user has authorized for the operational workflow.

## Example 1: Preview before shift change

Input packet:

```json
{
  "site": "North Plant",
  "line": "Packaging Line 2",
  "severity": "P1",
  "issue": "Temperature excursion detected during the final night-shift batch; investigation remains open.",
  "action_taken": "Line stopped and affected batch isolated.",
  "next_action": "Review historian data and determine whether the batch remains on quality hold.",
  "deadline": "Before 08:30 local time",
  "recipient_phone": "+15550100101",
  "escalation_phones": ["+15550100102"]
}
```

Preview:

```bash
python app.py examples/p1_temperature_excursion.json --dry-run
```

Expected behavior: print the handover packet, each planned CALL-E task and the structured result schema. No phone call is placed and no credential is required.

## Example 2: Accepted handover

The recipient answers, accurately restates the unresolved temperature excursion and required historian review, then says words equivalent to: "I have it. I'll review the historian now and update the hold decision by 08:15."

A valid structured result should contain evidence such as:

```json
{
  "reached_person": "yes",
  "understood_issue": "yes",
  "acknowledgement_quote": "I need to review the historian before the hold decision.",
  "ownership": "accepted",
  "ownership_quote": "I have it.",
  "eta_or_blocker": "Update by 08:15",
  "escalation_required": false
}
```

Expected host disposition: `accepted`.

The host may report that the incoming owner accepted the handover and give the ETA, but should mask the phone number and avoid dumping an unnecessary transcript.

## Example 3: Person answers but does not accept

The recipient understands the issue but says they are covering another line and cannot own the investigation.

```json
{
  "reached_person": "yes",
  "understood_issue": "yes",
  "acknowledgement_quote": "I understand Line 2 is still on hold pending historian review.",
  "ownership": "declined",
  "ownership_quote": "I can't take ownership of this one.",
  "eta_or_blocker": "Covering an active fault on Line 4",
  "escalation_required": true
}
```

Expected host disposition: `blocked` unless a separately authorized escalation contact remains in the declared chain. Do not reinterpret the read-back as acceptance.

## Example 4: Vague acknowledgement is not enough

The recipient says only "Okay, got it" and gives no restatement or explicit ownership commitment.

The structured result must not be promoted to `accepted`. Missing transcript-backed acknowledgement/ownership evidence should keep the handover open and require human follow-up or the next pre-declared contact.

## Example 5: Unknown call state

If the provider state is unknown or the host cannot tell whether the call is still active, do not immediately call again. Report the ambiguous state and reconcile it first. The idempotency key is a second line of defense, not permission to retry blindly.
