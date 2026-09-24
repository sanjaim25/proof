"""
Tests for Baseline Systems and Leakage Checks.
"""

import json
from pathlib import Path
import unittest

from src.evaluation.baseline_majority import MajorityBaseline
from src.evaluation.baseline_tfidf import TFIDFBaseline
from src.evaluation.check_leakage import normalize_text

WORKSPACE = Path(__file__).resolve().parents[2]
DEV_IDS_FILE = WORKSPACE / "data" / "processed" / "development_conversation_ids.txt"
VAL_IDS_FILE = WORKSPACE / "data" / "processed" / "validation_conversation_ids.txt"
GOLDEN_CSV = WORKSPACE / "data" / "golden" / "golden_set_v1.csv"

class TestBaselines(unittest.TestCase):
    
    def test_overlap_dev_golden(self):
        # We assume split_data has run
        if not DEV_IDS_FILE.exists() or not GOLDEN_CSV.exists():
            return
            
        with open(DEV_IDS_FILE, "r") as f:
            dev_ids = set(line.strip() for line in f if line.strip())
            
        import csv
        golden_ids = set()
        with open(GOLDEN_CSV, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                golden_ids.add(row["conversation_id"])
                
        overlap = dev_ids.intersection(golden_ids)
        self.assertEqual(len(overlap), 0, "Golden IDs found in Development set!")

    def test_overlap_val_golden(self):
        if not VAL_IDS_FILE.exists() or not GOLDEN_CSV.exists():
            return
            
        with open(VAL_IDS_FILE, "r") as f:
            val_ids = set(line.strip() for line in f if line.strip())
            
        import csv
        golden_ids = set()
        with open(GOLDEN_CSV, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                golden_ids.add(row["conversation_id"])
                
        overlap = val_ids.intersection(golden_ids)
        self.assertEqual(len(overlap), 0, "Golden IDs found in Validation set!")

    def test_majority_baseline_behavior(self):
        model = MajorityBaseline()
        # Override fit state
        model.majority_intent = "technical_issue"
        pred = model.predict("I need a refund")
        
        self.assertEqual(pred["intent"], "technical_issue")
        self.assertFalse(pred["escalate"])
        self.assertIn("Thanks", pred["reply"])

    def test_tfidf_low_similarity_fallback(self):
        model = TFIDFBaseline(threshold=0.99)
        # Add a dummy vector so it doesn't immediately return default
        model.vectors = [{"test": 1.0}]
        model.vocab = {"test"}
        model.corpus = [{"intent": "technical_issue", "escalate": False, "reply": "test"}]
        
        pred = model.predict("completely unknown message")
        
        # Sim is 0, threshold is 0.99
        self.assertEqual(pred["intent"], "other_or_unclear")
        self.assertTrue(pred["escalate"]) # Fallback escalate
        
    def test_tfidf_retrieval_behavior(self):
        model = TFIDFBaseline(k=3, threshold=0.1)
        model.vocab = {"broken", "item", "refund"}
        model.vectors = [
            {"broken": 1.0, "item": 1.0},
            {"refund": 1.0},
            {"broken": 1.0, "item": 1.0, "refund": 1.0}
        ]
        model.corpus = [
            {"intent": "issue_with_received_item", "escalate": True, "reply": "r1"},
            {"intent": "refund_request", "escalate": False, "reply": "r2"},
            {"intent": "issue_with_received_item", "escalate": False, "reply": "r3"}
        ]
        
        # Exact match to vector 0 and part of 2
        pred = model.predict("my broken item")
        
        # Nearest neighbors should be 0 and 2. 
        # Both are issue_with_received_item.
        self.assertEqual(pred["intent"], "issue_with_received_item")
        # Escalate vote: 1 True, 1 False -> tie? sum is 1, k=2 used (actually k=3, so 0, 2, 1).
        # Escalate is sum(escalates) >= k/2.0.
        # Top 3 are all of them. escalates = [True, False, False]. sum = 1. k=3. 1 >= 1.5 is False.
        self.assertFalse(pred["escalate"])
        
if __name__ == "__main__":
    unittest.main()
