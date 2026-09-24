"""
Local Browser-Based Human Annotation Tool for SupportProof.
Uses only the Python standard library.
"""

import csv
import json
import os
import random
import sys
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Dict, List, Optional

# ── Paths ──────────────────────────────────────────────────────────────────
WORKSPACE = Path(__file__).resolve().parents[2]
IN_JSONL  = WORKSPACE / "data" / "golden" / "golden_candidates.jsonl"
OUT_JSONL = WORKSPACE / "data" / "golden" / "golden_annotations.jsonl"
OUT_CSV   = WORKSPACE / "data" / "golden" / "golden_set.csv"
REPORT    = WORKSPACE / "reports" / "golden_annotation_progress.md"
GUIDE_MD  = WORKSPACE / "data" / "golden" / "ANNOTATION_GUIDE.md"

SEED = 42
PORT = 8080

# ── Taxonomy ───────────────────────────────────────────────────────────────
INTENTS = [
    {"id": "technical_issue", "desc": "App crashes, website errors, digital device problems."},
    {"id": "refund_request", "desc": "Explicitly asks for a refund, credits, or disputes a charge."},
    {"id": "delivery_delay", "desc": "Complains that an expected delivery is late/delayed."},
    {"id": "account_prime", "desc": "Account access (login, password) or Prime membership issues."},
    {"id": "order_tracking", "desc": "Asks for the location/status of an order, or a tracking link."},
    {"id": "return_request", "desc": "Asks how to return an item or requests a return label."},
    {"id": "issue_with_received_item", "desc": "Item is wrong, damaged, defective, or missing parts."},
    {"id": "missing_delivery", "desc": "Marked 'delivered' but not received, or confirmed stolen."},
    {"id": "gift_card_promotion", "desc": "Gift cards, claim codes, promo codes, or discounts."},
    {"id": "cancel_order", "desc": "Wants to cancel an order (that hasn't shipped yet)."},
    {"id": "other_or_unclear", "desc": "Noise, praise, ambiguous, or highly specific outliers."}
]

# ── State Management ───────────────────────────────────────────────────────

class AnnotationState:
    def __init__(self):
        self.candidates: List[dict] = []
        self.annotations: Dict[str, dict] = {}
        self.lock = threading.Lock()
        self.load_data()
        
    def load_data(self):
        if not IN_JSONL.exists():
            print(f"Error: {IN_JSONL} not found.")
            sys.exit(1)
            
        with open(IN_JSONL, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    self.candidates.append(json.loads(line))
                    
        # Deterministic shuffle
        rng = random.Random(SEED)
        rng.shuffle(self.candidates)
        
        # Load existing annotations
        if OUT_JSONL.exists():
            with open(OUT_JSONL, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        ann = json.loads(line)
                        if "example_id" in ann:
                            self.annotations[ann["example_id"]] = ann
                            
        self.update_outputs()

    def save_annotation(self, example_id: str, human_intent: str, human_escalate: bool, human_reason: str, annotation_notes: str):
        with self.lock:
            # Find candidate to merge
            candidate = next((c for c in self.candidates if c["example_id"] == example_id), None)
            if not candidate:
                raise ValueError("Candidate not found")
                
            ann = candidate.copy()
            ann["human_intent"] = human_intent
            ann["human_escalate"] = human_escalate
            ann["human_reason"] = human_reason
            ann["annotation_notes"] = annotation_notes
            
            self.annotations[example_id] = ann
            
            # Write JSONL
            OUT_JSONL.parent.mkdir(parents=True, exist_ok=True)
            with open(OUT_JSONL, "w", encoding="utf-8") as f:
                for cand in self.candidates:
                    eid = cand["example_id"]
                    if eid in self.annotations:
                        f.write(json.dumps(self.annotations[eid], ensure_ascii=False) + "\n")
                        
            self.update_outputs()

    def update_outputs(self):
        """Update CSV and Progress Report."""
        # Update CSV
        if self.candidates:
            fieldnames = [
                "example_id", "conversation_id", "created_at", "customer_message", 
                "previous_turns", "brand_response", "candidate_intents",
                "human_intent", "human_escalate", "human_reason", "annotation_notes"
            ]
            with open(OUT_CSV, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for cand in self.candidates:
                    eid = cand["example_id"]
                    row = self.annotations.get(eid, cand).copy()
                    
                    # Formatting for CSV
                    if isinstance(row.get("previous_turns"), list):
                        row["previous_turns"] = " | ".join(row["previous_turns"])
                    if isinstance(row.get("candidate_intents"), list):
                        row["candidate_intents"] = ", ".join(row["candidate_intents"])
                        
                    writer.writerow(row)
                    
        # Update Report
        total = len(self.candidates)
        completed = len(self.annotations)
        pct = (completed / total) * 100 if total > 0 else 0
        
        counts_by_intent = {i["id"]: 0 for i in INTENTS}
        escalate_yes = 0
        escalate_no = 0
        
        for ann in self.annotations.values():
            intent = ann.get("human_intent")
            if intent in counts_by_intent:
                counts_by_intent[intent] += 1
            if ann.get("human_escalate") is True:
                escalate_yes += 1
            elif ann.get("human_escalate") is False:
                escalate_no += 1
                
        md = [
            "# Golden Annotation Progress",
            f"\n- **Total Examples**: {total}",
            f"- **Completed**: {completed}",
            f"- **Remaining**: {total - completed}",
            f"- **Progress**: {pct:.1f}%",
            "\n## Escalations",
            f"- **Yes**: {escalate_yes}",
            f"- **No**: {escalate_no}",
            "\n## Intents"
        ]
        for intent_id, count in sorted(counts_by_intent.items(), key=lambda x: x[1], reverse=True):
            md.append(f"- `{intent_id}`: {count}")
            
        REPORT.write_text("\n".join(md), encoding="utf-8")

STATE = AnnotationState()

# ── Frontend HTML ──────────────────────────────────────────────────────────

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SupportProof Annotation</title>
    <style>
        body { font-family: system-ui, -apple-system, sans-serif; margin: 0; padding: 20px; background: #f5f7fa; color: #333; }
        .container { max-width: 1000px; margin: 0 auto; display: flex; gap: 20px; }
        .panel { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .left-panel { flex: 2; }
        .right-panel { flex: 1; position: sticky; top: 20px; height: max-content; }
        
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .progress-bar { background: #eee; height: 10px; border-radius: 5px; width: 200px; overflow: hidden; }
        .progress-fill { background: #4caf50; height: 100%; transition: width 0.3s; }
        
        .chat-bubble { padding: 12px 16px; border-radius: 12px; margin-bottom: 12px; max-width: 85%; }
        .chat-brand { background: #f0f0f0; border-bottom-left-radius: 4px; margin-right: auto; }
        .chat-customer { background: #e3f2fd; border-bottom-right-radius: 4px; margin-left: auto; border: 2px solid #2196f3; }
        .chat-target { background: #bbdefb; font-weight: 500; font-size: 1.1em; border: 2px solid #1976d2; }
        
        .meta { font-size: 0.85em; color: #666; margin-bottom: 4px; }
        
        .form-group { margin-bottom: 15px; }
        label { display: block; font-weight: 600; margin-bottom: 8px; }
        .radio-group { display: flex; flex-direction: column; gap: 8px; max-height: 400px; overflow-y: auto; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
        .radio-item { display: flex; align-items: flex-start; gap: 8px; padding: 8px; border-radius: 4px; cursor: pointer; }
        .radio-item:hover { background: #f5f5f5; }
        .intent-desc { font-size: 0.85em; color: #666; display: block; margin-top: 2px; }
        
        textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; font-family: inherit; resize: vertical; box-sizing: border-box; }
        
        .nav-buttons { display: flex; justify-content: space-between; margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee; }
        button { padding: 10px 16px; border: none; border-radius: 4px; cursor: pointer; font-weight: 600; font-size: 14px; }
        .btn-primary { background: #2196f3; color: white; }
        .btn-secondary { background: #e0e0e0; color: #333; }
        button:disabled { opacity: 0.5; cursor: not-allowed; }
        
        .jump-nav { display: flex; align-items: center; gap: 10px; }
        select { padding: 6px; border-radius: 4px; border: 1px solid #ddd; }
        
        .badge { display: inline-block; padding: 2px 6px; border-radius: 10px; font-size: 12px; font-weight: bold; }
        .badge-done { background: #c8e6c9; color: #2e7d32; }
        .badge-todo { background: #ffecb3; color: #f57f17; }
        
        #toast { position: fixed; bottom: 20px; right: 20px; background: #323232; color: white; padding: 12px 24px; border-radius: 4px; display: none; }
    </style>
</head>
<body>
    <div class="header">
        <h1>SupportProof Annotation</h1>
        <div>
            <div style="text-align: right; margin-bottom: 4px;" id="progress-text">Loading...</div>
            <div class="progress-bar"><div class="progress-fill" id="progress-fill" style="width: 0%"></div></div>
        </div>
    </div>
    
    <div class="container">
        <div class="panel left-panel">
            <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
                <div>
                    <strong>Example ID:</strong> <span id="example-id"></span><br>
                    <strong>Conv ID:</strong> <span id="conv-id"></span>
                </div>
                <div class="jump-nav">
                    <select id="jump-select" onchange="jumpTo(this.value)"></select>
                    <button class="btn-secondary" onclick="jumpToUnlabeled()">Go to Next Unlabeled</button>
                </div>
            </div>
            
            <div style="background: #fafafa; padding: 15px; border-radius: 8px; border: 1px solid #eee;">
                <h3>Conversation Context</h3>
                <div id="chat-container"></div>
            </div>
        </div>
        
        <div class="panel right-panel">
            <form id="annotation-form" onsubmit="saveAndNext(event)">
                <div class="form-group">
                    <label>Intent <span style="color:red">*</span></label>
                    <div class="radio-group" id="intent-group">
                        <!-- Populated by JS -->
                    </div>
                </div>
                
                <div class="form-group">
                    <label>Escalate to Human? <span style="color:red">*</span></label>
                    <div style="display: flex; gap: 15px;">
                        <label style="font-weight: normal;"><input type="radio" name="escalate" value="true" required> Yes</label>
                        <label style="font-weight: normal;"><input type="radio" name="escalate" value="false" required> No</label>
                    </div>
                </div>
                
                <div class="form-group">
                    <label>Escalation Reason</label>
                    <textarea name="reason" rows="2" placeholder="Why does this need human intervention?"></textarea>
                </div>
                
                <div class="form-group">
                    <label>Annotation Notes</label>
                    <textarea name="notes" rows="2" placeholder="Any edge case notes?"></textarea>
                </div>
                
                <div class="nav-buttons">
                    <button type="button" class="btn-secondary" id="btn-prev" onclick="navigate(-1)">Previous</button>
                    <button type="submit" class="btn-primary" id="btn-save">Save & Next</button>
                </div>
            </form>
        </div>
    </div>
    
    <div id="toast">Saved!</div>
    
    <script>
        const INTENTS = [
            {"id": "technical_issue", "desc": "App crashes, website errors, digital device problems."},
            {"id": "refund_request", "desc": "Explicitly asks for a refund, credits, or disputes a charge."},
            {"id": "delivery_delay", "desc": "Complains that an expected delivery is late/delayed."},
            {"id": "account_prime", "desc": "Account access (login, password) or Prime membership issues."},
            {"id": "order_tracking", "desc": "Asks for the location/status of an order, or a tracking link."},
            {"id": "return_request", "desc": "Asks how to return an item or requests a return label."},
            {"id": "issue_with_received_item", "desc": "Item is wrong, damaged, defective, or missing parts."},
            {"id": "missing_delivery", "desc": "Marked 'delivered' but not received, or confirmed stolen."},
            {"id": "gift_card_promotion", "desc": "Gift cards, claim codes, promo codes, or discounts."},
            {"id": "cancel_order", "desc": "Wants to cancel an order (that hasn't shipped yet)."},
            {"id": "other_or_unclear", "desc": "Noise, praise, ambiguous, or highly specific outliers."}
        ];
        
        let state = { candidates: [], annotations: {}, currentIndex: 0 };
        
        async function loadData() {
            const res = await fetch('/api/data');
            state = await res.json();
            
            // Populate intents
            const ig = document.getElementById('intent-group');
            ig.innerHTML = INTENTS.map(i => `
                <label class="radio-item">
                    <input type="radio" name="intent" value="${i.id}" required>
                    <div>
                        <strong>${i.id}</strong>
                        <span class="intent-desc">${i.desc}</span>
                    </div>
                </label>
            `).join('');
            
            jumpToUnlabeled(true);
        }
        
        function updateUI() {
            if (state.candidates.length === 0) return;
            
            const cand = state.candidates[state.currentIndex];
            const ann = state.annotations[cand.example_id];
            
            // Progress
            const completed = Object.keys(state.annotations).length;
            const total = state.candidates.length;
            const pct = total ? (completed / total * 100) : 0;
            document.getElementById('progress-text').innerText = `${completed} / ${total} completed`;
            document.getElementById('progress-fill').style.width = `${pct}%`;
            
            // Header
            document.getElementById('example-id').innerText = cand.example_id;
            document.getElementById('conv-id').innerText = cand.conversation_id;
            
            // Chat Context
            let chatHTML = '';
            for (let t of cand.previous_turns || []) {
                // Heuristic styling for previous turns (alternating, roughly)
                chatHTML += `<div class="chat-bubble chat-brand"><div class="meta">Context Turn</div>${escapeHTML(t)}</div>`;
            }
            
            chatHTML += `<div class="chat-bubble chat-customer chat-target"><div class="meta">Target Message - ${cand.created_at || ''}</div>${escapeHTML(cand.customer_message)}</div>`;
            
            if (cand.brand_response) {
                chatHTML += `<div class="chat-bubble chat-brand"><div class="meta">Historical Brand Response</div>${escapeHTML(cand.brand_response)}</div>`;
            }
            
            document.getElementById('chat-container').innerHTML = chatHTML;
            
            // Form
            const form = document.getElementById('annotation-form');
            form.reset();
            if (ann) {
                if (ann.human_intent) form.intent.value = ann.human_intent;
                if (ann.human_escalate !== null && ann.human_escalate !== undefined) {
                    form.escalate.value = ann.human_escalate.toString();
                }
                if (ann.human_reason) form.reason.value = ann.human_reason;
                if (ann.annotation_notes) form.notes.value = ann.annotation_notes;
            }
            
            // Nav Dropdown
            const select = document.getElementById('jump-select');
            select.innerHTML = state.candidates.map((c, idx) => {
                const isDone = !!state.annotations[c.example_id];
                const marker = isDone ? '✓' : '○';
                return `<option value="${idx}" ${idx === state.currentIndex ? 'selected' : ''}>${idx + 1}. ${c.example_id} ${marker}</option>`;
            }).join('');
            
            document.getElementById('btn-prev').disabled = state.currentIndex === 0;
            document.getElementById('btn-save').innerText = state.currentIndex === total - 1 ? 'Save' : 'Save & Next';
        }
        
        async function saveAndNext(e) {
            e.preventDefault();
            const form = document.getElementById('annotation-form');
            const cand = state.candidates[state.currentIndex];
            
            const payload = {
                example_id: cand.example_id,
                human_intent: form.intent.value,
                human_escalate: form.escalate.value === 'true',
                human_reason: form.reason.value || null,
                annotation_notes: form.notes.value || null
            };
            
            const res = await fetch('/api/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            if (res.ok) {
                state.annotations[cand.example_id] = payload;
                showToast();
                navigate(1);
            }
        }
        
        function navigate(dir) {
            const nextIdx = state.currentIndex + dir;
            if (nextIdx >= 0 && nextIdx < state.candidates.length) {
                state.currentIndex = nextIdx;
                updateUI();
                window.scrollTo(0, 0);
            }
        }
        
        function jumpTo(idx) {
            state.currentIndex = parseInt(idx, 10);
            updateUI();
            window.scrollTo(0, 0);
        }
        
        function jumpToUnlabeled(initialLoad=false) {
            for (let i = 0; i < state.candidates.length; i++) {
                if (!state.annotations[state.candidates[i].example_id]) {
                    state.currentIndex = i;
                    updateUI();
                    return;
                }
            }
            if (!initialLoad) alert("All examples are labeled!");
            else updateUI();
        }
        
        function showToast() {
            const toast = document.getElementById('toast');
            toast.style.display = 'block';
            setTimeout(() => toast.style.display = 'none', 2000);
        }
        
        function escapeHTML(str) {
            if (!str) return '';
            return str.replace(/[&<>'"]/g, 
                tag => ({
                    '&': '&amp;',
                    '<': '&lt;',
                    '>': '&gt;',
                    "'": '&#39;',
                    '"': '&quot;'
                }[tag])
            );
        }
        
        window.onload = loadData;
    </script>
</body>
</html>
"""

# ── Server ─────────────────────────────────────────────────────────────────

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode("utf-8"))
        elif self.path == "/api/data":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            
            # Remove candidate_intents from frontend to avoid bias
            safe_cands = []
            for c in STATE.candidates:
                c_copy = c.copy()
                c_copy.pop("candidate_intents", None)
                safe_cands.append(c_copy)
                
            payload = {
                "candidates": safe_cands,
                "annotations": STATE.annotations
            }
            self.wfile.write(json.dumps(payload).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()
            
    def do_POST(self):
        if self.path == "/api/save":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode("utf-8"))
            
            try:
                STATE.save_annotation(
                    data["example_id"],
                    data["human_intent"],
                    data["human_escalate"],
                    data.get("human_reason"),
                    data.get("annotation_notes")
                )
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success"}).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

def run_server():
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f"\n=======================================================")
    print(f"SUPPORTPROOF ANNOTATION TOOL RUNNING")
    print(f"=======================================================")
    print(f"\nPlease open your browser and navigate to:")
    print(f"http://localhost:{PORT}")
    print(f"\nTo stop the server, press Ctrl+C")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
