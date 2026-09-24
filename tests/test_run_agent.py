import json
import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

import src.evaluation.run_agent as run_agent
from src.agent.agent import SupportProofAgent

@pytest.fixture
def mock_workspace(tmp_path):
    with patch("src.evaluation.run_agent.WORKSPACE", tmp_path), \
         patch("src.evaluation.run_agent.GOLDEN_CSV", tmp_path / "data" / "golden" / "golden_set_v1.csv"), \
         patch("src.evaluation.run_agent.OUT_PREDICTIONS", tmp_path / "data" / "processed" / "agent_predictions_v1.1.jsonl"), \
         patch("src.evaluation.run_agent.METADATA_JSON", tmp_path / "data" / "processed" / "agent_evaluation_metadata_v1.1.json"), \
         patch("src.evaluation.run_agent.REPORT_MD", tmp_path / "reports" / "agent_results_v1.1.md"):
        
        # Setup fake golden set
        golden_path = tmp_path / "data" / "golden"
        golden_path.mkdir(parents=True)
        with open(golden_path / "golden_set_v1.csv", "w", encoding="utf-8") as f:
            f.write("example_id,human_intent,human_escalate,customer_message\n")
            for i in range(5):
                f.write(f"gold_0{i},intent_A,False,msg {i}\n")
                
        yield tmp_path

@pytest.fixture
def mock_agent():
    with patch("src.evaluation.run_agent.SupportProofAgent") as mock_cls:
        agent_instance = MagicMock()
        mock_cls.return_value = agent_instance
        
        # Mock process to return success
        def mock_process(req):
            return {
                "intent": "intent_A",
                "intent_confidence": 0.9,
                "reply": "reply",
                "escalate": False,
                "escalation_reason": "",
                "evidence": [],
                "retrieval_scores": [0.8],
                "retrieval_confidence": "strong"
            }
        agent_instance.process.side_effect = mock_process
        yield agent_instance

def test_fresh_run_creates_metadata(mock_workspace, mock_agent):
    with patch("sys.argv", ["run_agent.py"]):
        run_agent.main()
    
    assert run_agent.METADATA_JSON.exists()
    assert run_agent.OUT_PREDICTIONS.exists()
    
    with open(run_agent.METADATA_JSON, "r") as f:
        meta = json.load(f)
        assert meta["k"] == 2
        assert meta["threshold"] == 0.55

    # Should have 5 predictions
    lines = run_agent.OUT_PREDICTIONS.read_text().strip().split("\n")
    assert len(lines) == 5

def test_existing_file_without_resume_exits(mock_workspace, mock_agent):
    run_agent.OUT_PREDICTIONS.parent.mkdir(parents=True, exist_ok=True)
    run_agent.OUT_PREDICTIONS.write_text("fake")
    
    with patch("sys.argv", ["run_agent.py"]):
        with pytest.raises(SystemExit):
            run_agent.main()

def test_resume_configuration_mismatch(mock_workspace, mock_agent):
    run_agent.OUT_PREDICTIONS.parent.mkdir(parents=True, exist_ok=True)
    run_agent.OUT_PREDICTIONS.write_text("fake")
    run_agent.METADATA_JSON.write_text(json.dumps({"model": "wrong", "k": 2, "threshold": 0.55}))
    
    with patch("sys.argv", ["run_agent.py", "--resume"]):
        with pytest.raises(AssertionError, match="Model mismatch"):
            run_agent.main()

def test_rate_limit_breaks_loop_and_resume_skips(mock_workspace, mock_agent):
    # First run hits rate limit on example 3 (index 2)
    def mock_process_rate_limit(req):
        if "msg 2" in req.customer_message:
            return {"api_error": "429 rate limit exceeded"}
        return {
            "intent": "intent_A",
            "intent_confidence": 0.9,
            "reply": "reply",
            "escalate": False,
            "escalation_reason": "",
            "evidence": [],
            "retrieval_scores": [0.8],
            "retrieval_confidence": "strong"
        }
    mock_agent.process.side_effect = mock_process_rate_limit
    
    with patch("sys.argv", ["run_agent.py"]):
        run_agent.main()
        
    lines = run_agent.OUT_PREDICTIONS.read_text().strip().split("\n")
    assert len(lines) == 2 # gold_00 and gold_01 processed
    
    # Second run with resume
    def mock_process_resume(req):
        assert "msg 0" not in req.customer_message
        assert "msg 1" not in req.customer_message
        return {
            "intent": "intent_A",
            "intent_confidence": 0.9,
            "reply": "reply",
            "escalate": False,
            "escalation_reason": "",
            "evidence": [],
            "retrieval_scores": [0.8],
            "retrieval_confidence": "strong"
        }
    mock_agent.process.side_effect = mock_process_resume
    
    with patch("sys.argv", ["run_agent.py", "--resume"]):
        run_agent.main()
        
    lines = run_agent.OUT_PREDICTIONS.read_text().strip().split("\n")
    assert len(lines) == 5 # 2 from before + 3 new (gold_02, 03, 04)

def test_api_error_preserved(mock_workspace, mock_agent):
    def mock_process_api_error(req):
        if "msg 1" in req.customer_message:
            return {"api_error": "json_validate_failed"}
        return {
            "intent": "intent_A",
            "intent_confidence": 0.9,
            "reply": "reply",
            "escalate": False,
            "escalation_reason": "",
            "evidence": [],
            "retrieval_scores": [0.8],
            "retrieval_confidence": "strong"
        }
    mock_agent.process.side_effect = mock_process_api_error
    
    with patch("sys.argv", ["run_agent.py"]):
        run_agent.main()
        
    lines = run_agent.OUT_PREDICTIONS.read_text().strip().split("\n")
    assert len(lines) == 5
    
    # verify gold_01 has api_error
    data = [json.loads(l) for l in lines]
    err_record = next(d for d in data if d["example_id"] == "gold_01")
    assert err_record.get("api_error") == "json_validate_failed"
