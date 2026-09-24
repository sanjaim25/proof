"""
Tests for golden evaluation set generation.
"""

import csv
import json
from pathlib import Path
import unittest
from src.evaluation.build_golden import (
    guess_candidate_intents,
    normalize_text
)

class TestBuildGolden(unittest.TestCase):
    
    def setUp(self):
        self.workspace = Path(__file__).resolve().parents[2]
        self.jsonl_path = self.workspace / "data" / "golden" / "golden_candidates.jsonl"
        self.csv_path = self.workspace / "data" / "golden" / "golden_set.csv"

    def test_heuristics(self):
        self.assertIn("delivery_delay", guess_candidate_intents("my package is late"))
        self.assertIn("missing_delivery", guess_candidate_intents("tracking says delivered but it's empty box"))
        
        # Test difficult/multiple intents
        intents = guess_candidate_intents("my order is late and I want a refund")
        self.assertIn("delivery_delay", intents)
        self.assertIn("refund_request", intents)

    def test_normalize_text(self):
        self.assertEqual(
            normalize_text("@AmazonHelp Hello! http://link.com"),
            "hello"
        )
        self.assertEqual(
            normalize_text("UPPERCASE... words-with-punct!"),
            "uppercasewordswithpunct"
        )

    def test_golden_output_validity(self):
        # Only run if output exists
        if not self.jsonl_path.exists():
            return
            
        records = []
        with open(self.jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                records.append(json.loads(line))
                
        # 1. Exactly 200 examples
        self.assertEqual(len(records), 200)
        
        # 2. Unique example IDs
        ids = [r["example_id"] for r in records]
        self.assertEqual(len(ids), len(set(ids)))
        
        # 3. No duplicate customer messages (normalized)
        messages = [normalize_text(r["customer_message"]) for r in records]
        self.assertEqual(len(messages), len(set(messages)))
        
        # 4. Required fields exist and annotation fields are null
        for r in records:
            self.assertIn("example_id", r)
            self.assertIn("conversation_id", r)
            self.assertIn("customer_message", r)
            self.assertIn("previous_turns", r)
            self.assertIn("brand_response", r)
            self.assertIn("candidate_intents", r)
            
            self.assertIsNone(r["human_intent"])
            self.assertIsNone(r["human_escalate"])
            self.assertIsNone(r["human_reason"])
            self.assertIsNone(r["annotation_notes"])

if __name__ == "__main__":
    unittest.main()
