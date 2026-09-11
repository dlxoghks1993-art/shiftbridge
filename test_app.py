import unittest

from app import Incident, RESULT_SCHEMA, build_call_task


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
        }

    def test_incident_accepts_valid_payload(self):
        incident = Incident.from_dict(self.payload)
        self.assertEqual(incident.severity, "P1")
        self.assertEqual(incident.recipient_phone, "+15551234567")

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

    def test_call_task_contains_guardrails_and_operational_facts(self):
        task = build_call_task(Incident.from_dict(self.payload))
        self.assertIn("Temperature excursion detected", task)
        self.assertIn("accept ownership", task)
        self.assertIn("Do not invent facts or commitments", task)
        self.assertIn("escalation_required=true", task)

    def test_result_schema_requires_judge_visible_outcomes(self):
        required = set(RESULT_SCHEMA["required"])
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
