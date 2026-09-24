"""
Tests for the local browser-based annotation tool.
"""

import json
import os
import tempfile
from pathlib import Path
import unittest

import src.evaluation.annotate as annotate_module
from src.evaluation.annotate import AnnotationState

class TestAnnotationTool(unittest.TestCase):
    
    def setUp(self):
        # Create temp files for output to avoid corrupting real user data
        self.temp_dir = tempfile.TemporaryDirectory()
        self.mock_out_jsonl = Path(self.temp_dir.name) / "mock_ann.jsonl"
        self.mock_out_csv = Path(self.temp_dir.name) / "mock_csv.csv"
        self.mock_out_report = Path(self.temp_dir.name) / "mock_report.md"
        
        # Patch the paths
        annotate_module.OUT_JSONL = self.mock_out_jsonl
        annotate_module.OUT_CSV = self.mock_out_csv
        annotate_module.REPORT = self.mock_out_report
        
        self.state = AnnotationState()
        
    def tearDown(self):
        self.temp_dir.cleanup()
        
    def test_load_data(self):
        self.assertEqual(len(self.state.candidates), 200)
        self.assertIn("example_id", self.state.candidates[0])
        
    def test_save_annotation_updates_state(self):
        example = self.state.candidates[0]
        eid = example["example_id"]
        
        self.state.save_annotation(
            example_id=eid,
            human_intent="technical_issue",
            human_escalate=True,
            human_reason="Needs dev team",
            annotation_notes="Tricky"
        )
        
        self.assertIn(eid, self.state.annotations)
        ann = self.state.annotations[eid]
        self.assertEqual(ann["human_intent"], "technical_issue")
        self.assertEqual(ann["human_escalate"], True)
        self.assertEqual(ann["human_reason"], "Needs dev team")
        self.assertEqual(ann["annotation_notes"], "Tricky")
        
        # Verify JSONL was written
        with open(self.mock_out_jsonl, "r", encoding="utf-8") as f:
            lines = f.readlines()
            self.assertGreater(len(lines), 0)
            
        # Verify CSV was updated
        import csv
        with open(self.mock_out_csv, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)
            self.assertEqual(len(rows), 201) # header + 200 examples
            
        # Verify Report was updated
        with open(self.mock_out_report, "r", encoding="utf-8") as f:
            report_content = f.read()
            self.assertIn("- **Completed**: ", report_content)
            self.assertIn("technical_issue", report_content)

if __name__ == "__main__":
    unittest.main()
