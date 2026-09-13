import unittest
from types import SimpleNamespace

from app import (
    Incident,
    RESULT_SCHEMA,
    _call_once,
    _handover_disposition,
    _idempotency_key,
    _needs_escalation,
    _read_call_field,
    build_call_task,
)


class ShiftBridgeTests(unittest.TestCase):
    def setUp(self):
        self.payload = {
            "site": "Plant A",
            "line": "Packaging Line 2",
            "severity": "P1",
            "issue": "Temperature excursion detected",
            "action_taken": "Line stopped and affected batch isolated",
            "next_action": "Inspect root cause and approve restart",
            "deadline": "06:30 local time",
            "recipient_phone": "+15551234567",
            "escalation_phones": ["+15557654321"],
        }

    def test_incident_accepts_valid_payload(self):
        incident = Incident.from_dict(self.payload)
        self.assertEqual(incident.severity, "P1")
        self.assertEqual(incident.recipient_phone, "+15551234567")
        self.assertEqual(incident.escalation_phones, ["+15557654321"])

    def test_incident_rejects_missing_field(self):
        payload = dict(self.payload)
        payload.pop("deadline")
        with self.assertRaisesRegex(ValueError, "Missing incident fields: deadline"):
            Incident.from_dict(payload)

    def test_incident_rejects_invalid_severity(self):
        payload = dict(self.payload)
        payload["severity"] = "P0"
        with self.assertRaisesRegex(ValueError, "severity must be P1, P2, or P3"):
            Incident.from_dict(payload)

    def test_incident_rejects_non_e164_phone(self):
        payload = dict(self.payload)
        payload["recipient_phone"] = "01012345678"
        with self.assertRaisesRegex(ValueError, "E.164"):
            Incident.from_dict(payload)

    def test_incident_rejects_bad_escalation_phone(self):
        payload = dict(self.payload)
        payload["escalation_phones"] = ["01099999999"]
        with self.assertRaisesRegex(ValueError, "E.164"):
            Incident.from_dict(payload)

    def test_call_task_contains_guardrails_and_operational_facts(self):
        task = build_call_task(Incident.from_dict(self.payload))
        self.assertIn("Temperature excursion detected", task)
        self.assertIn("accept ownership", task)
        self.assertIn("automated ShiftBridge assistant", task)
        self.assertIn("Do not invent facts or commitments", task)
        self.assertIn("escalation_required=true", task)

    def test_call_field_supports_mapping_and_sdk_object_shapes(self):
        self.assertEqual(_read_call_field({"status": "completed"}, "status"), "completed")
        response = SimpleNamespace(status="completed", structured_result={"ownership": "accepted"})
        self.assertEqual(_read_call_field(response, "status"), "completed")
        self.assertEqual(_read_call_field(response, "structured_result"), {"ownership": "accepted"})
        self.assertIsNone(_read_call_field(response, "missing"))

    def test_idempotency_key_is_stable_and_target_specific(self):
        incident = Incident.from_dict(self.payload)
        same = Incident.from_dict(dict(self.payload))
        changed = Incident.from_dict({**self.payload, "recipient_phone": "+15550000000"})
        self.assertEqual(_idempotency_key(incident), _idempotency_key(same))
        self.assertNotEqual(_idempotency_key(incident), _idempotency_key(changed))
        self.assertTrue(_idempotency_key(incident).startswith("shiftbridge-"))

    def test_call_once_passes_explicit_recipient_and_idempotency_key(self):
        captured = {}

        class FakeCalls:
            def create_and_wait(self, **kwargs):
                captured.update(kwargs)
                return {
                    "status": "completed",
                    "structured_result": {
                        "reached_person": "yes",
                        "understood_issue": "yes",
                        "ownership": "accepted",
                        "eta_or_blocker": "20 minutes",
                        "escalation_required": False,
                    },
                }

        fake_client = SimpleNamespace(calls=FakeCalls())
        incident = Incident.from_dict(self.payload)
        result = _call_once(fake_client, incident)
        self.assertEqual(captured["recipient"], {"phone": "+15551234567"})
        self.assertEqual(captured["idempotency_key"], _idempotency_key(incident))
        self.assertEqual(captured["result_schema"], RESULT_SCHEMA)
        self.assertEqual(result["phone"], "+15551234567")

    def test_closed_handoff_does_not_escalate(self):
        result = {
            "structured_result": {
                "reached_person": "yes",
                "understood_issue": "yes",
                "ownership": "accepted",
                "eta_or_blocker": "20 minutes",
                "escalation_required": False,
            }
        }
        self.assertFalse(_needs_escalation(result))
        self.assertEqual(_handover_disposition(result), "accepted")

    def test_declined_ownership_escalates(self):
        result = {
            "structured_result": {
                "reached_person": "yes",
                "understood_issue": "yes",
                "ownership": "declined",
                "eta_or_blocker": "Not responsible for this line",
                "escalation_required": True,
            }
        }
        self.assertTrue(_needs_escalation(result))
        self.assertEqual(_handover_disposition(result), "blocked")

    def test_unreached_maps_to_unreached_before_chain_exhaustion(self):
        result = {
            "structured_result": {
                "reached_person": "no",
                "understood_issue": "unknown",
                "ownership": "unknown",
                "eta_or_blocker": "No answer",
                "escalation_required": True,
            }
        }
        self.assertEqual(_handover_disposition(result), "unreached")

    def test_exhausted_escalation_chain_requires_supervisor(self):
        result = {
            "structured_result": {
                "reached_person": "no",
                "understood_issue": "unknown",
                "ownership": "unknown",
                "eta_or_blocker": "No answer",
                "escalation_required": True,
            }
        }
        self.assertEqual(_handover_disposition(result, chain_exhausted=True), "needs_supervisor")

    def test_result_schema_requires_judge_visible_outcomes(self):
        required = set(RESULT_SCHEMA["required"])
        self.assertFalse(RESULT_SCHEMA["additionalProperties"])
        self.assertEqual(
            required,
            {
                "reached_person",
                "understood_issue",
                "ownership",
                "eta_or_blocker",
                "escalation_required",
            },
        )


if __name__ == "__main__":
    unittest.main()
