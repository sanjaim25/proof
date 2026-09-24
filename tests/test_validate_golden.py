"""
Tests for the Golden Set Validation Script.
"""

import json
import tempfile
from pathlib import Path
import unittest

import src.evaluation.validate_golden as validate_module

class TestValidateGolden(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.mock_in_jsonl = Path(self.temp_dir.name) / "mock_in.jsonl"
        
        validate_module.IN_JSONL = self.mock_in_jsonl
        
    def tearDown(self):
        self.temp_dir.cleanup()
        
    def write_mock_records(self, records: list):
        with open(self.mock_in_jsonl, "w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(r) + "\n")
                
    def get_valid_record(self, idx: int) -> dict:
        return {
            "example_id": f"gold_{idx:04d}",
            "conversation_id": f"conv_{idx}",
            "customer_message": f"This is a valid test message {idx}",
            "human_intent": "technical_issue",
            "human_escalate": False,
            "human_reason": None,
            "annotation_notes": "Test"
        }

    def test_fails_on_incorrect_count(self):
        records = [self.get_valid_record(i) for i in range(199)]
        self.write_mock_records(records)
        with self.assertRaisesRegex(ValueError, "Expected 200 examples"):
            validate_module.validate_data()

    def test_fails_on_missing_fields(self):
        records = [self.get_valid_record(i) for i in range(200)]
        del records[0]["human_intent"]
        self.write_mock_records(records)
        with self.assertRaisesRegex(ValueError, "missing fields"):
            validate_module.validate_data()

    def test_fails_on_duplicate_example_id(self):
        records = [self.get_valid_record(i) for i in range(200)]
        records[1]["example_id"] = records[0]["example_id"]
        self.write_mock_records(records)
        with self.assertRaisesRegex(ValueError, "Duplicate example_id"):
            validate_module.validate_data()

    def test_fails_on_duplicate_messages(self):
        records = [self.get_valid_record(i) for i in range(200)]
        records[1]["customer_message"] = records[0]["customer_message"]
        self.write_mock_records(records)
        with self.assertRaisesRegex(ValueError, "Duplicate customer message"):
            validate_module.validate_data()

    def test_fails_on_invalid_intent(self):
        records = [self.get_valid_record(i) for i in range(200)]
        records[0]["human_intent"] = "magic_pizza"
        self.write_mock_records(records)
        with self.assertRaisesRegex(ValueError, "Invalid intent"):
            validate_module.validate_data()

    def test_fails_on_invalid_escalate(self):
        records = [self.get_valid_record(i) for i in range(200)]
        records[0]["human_escalate"] = "Maybe"
        self.write_mock_records(records)
        with self.assertRaisesRegex(ValueError, "Invalid escalate value"):
            validate_module.validate_data()

    def test_warnings(self):
        records = [self.get_valid_record(i) for i in range(200)]
        
        # Trigger short message warning
        records[0]["customer_message"] = "hi"
        # Trigger other_or_unclear warning
        records[1]["human_intent"] = "other_or_unclear"
        # Trigger empty reason warning on Escalate=Yes
        records[2]["human_escalate"] = True
        records[2]["human_reason"] = ""
        
        self.write_mock_records(records)
        stats = validate_module.validate_data()
        
        self.assertTrue(any("short customer message" in w for w in stats["warnings"]))
        self.assertTrue(any("other_or_unclear" in w for w in stats["warnings"]))
        self.assertTrue(any("human_reason is empty" in w for w in stats["warnings"]))

if __name__ == "__main__":
    unittest.main()
