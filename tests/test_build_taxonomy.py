"""
Tests for the taxonomy proposal schema and generation.
"""

import json
import os
import unittest
from pathlib import Path
from src.intent.build_taxonomy import (
    is_support_message,
    find_matches,
    IntentDefinition
)

class TestTaxonomyBuilder(unittest.TestCase):
    
    def test_is_support_message(self):
        self.assertFalse(is_support_message("thank you very much amazon"))
        self.assertTrue(is_support_message("thank you very much amazon, but my package is late"))
        self.assertFalse(is_support_message("http://amazon.com/help"))
        
    def test_find_matches_operational_boundaries(self):
        intent = IntentDefinition(
            id_str="missing_delivery",
            name="Missing Delivery",
            description="",
            in_scope=[],
            out_of_scope=[],
            confusions=[],
            keywords=["says delivered", "stolen"],
            negations=["late", "delay"],
            action="KEEP"
        )
        
        messages = [
            "my package says delivered but I can't find it", # strong match
            "my package was stolen from my porch",           # strong match
            "tracking says delivered but maybe it's just late?", # false positive (contains "late")
            "random message about amazon prime"              # no match
        ]
        
        strong, false_pos = find_matches(messages, intent)
        
        self.assertEqual(len(strong), 2)
        self.assertEqual(len(false_pos), 1)
        self.assertIn("my package says delivered but I can't find it", strong)
        self.assertIn("my package was stolen from my porch", strong)
        self.assertIn("tracking says delivered but maybe it's just late?", false_pos)

    def test_taxonomy_json_schema(self):
        # Only run this test if the JSON has been generated
        json_path = Path(__file__).resolve().parents[2] / "data" / "processed" / "taxonomy_proposal.json"
        if not json_path.exists():
            return
            
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        self.assertIn("version", data)
        self.assertEqual(data["status"], "human_review_required")
        self.assertIn("intents", data)
        
        for intent in data["intents"]:
            self.assertIn("intent_id", intent)
            self.assertIn("name", intent)
            self.assertIn("description", intent)
            self.assertIn("in_scope", intent)
            self.assertIn("out_of_scope", intent)
            self.assertIn("representative_examples", intent)
            self.assertIn("confusable_intents", intent)
            self.assertIn("estimated_prevalence", intent)
            self.assertIsInstance(intent["representative_examples"], list)

if __name__ == "__main__":
    unittest.main()
