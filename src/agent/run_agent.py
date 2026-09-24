"""
Interactive CLI for testing the SupportProof Agent.
"""

import sys
from src.agent.agent import SupportProofAgent
from src.agent.schemas import AgentRequest

def main():
    print("Initializing SupportProof Agent v0 (loading retrieval corpus)...")
    agent = SupportProofAgent(k=5, sim_threshold=0.55)
    agent.retriever.fit()
    print("Ready.\n")
    
    while True:
        try:
            msg = input("Customer message (or 'quit'): ")
            if msg.lower() in ('quit', 'exit', 'q'):
                break
            if not msg.strip():
                continue
                
            req = AgentRequest(customer_message=msg)
            res = agent.process(req)
            
            print("\n--------------------------------------------------")
            print(f"Intent:      {res['intent']} (Conf: {res['intent_confidence']:.2f})")
            print(f"Escalate:    {res['escalate']}")
            if res['escalate']:
                print(f"Reason:      {res['escalation_reason']}")
                
            print(f"\nDraft Reply: {res['reply']}")
            
            if res.get('validation_failures'):
                print("\n[!] VALIDATION FAILURES:")
                for f in res['validation_failures']:
                    print(f"  - {f}")
                print(f"Original Draft: {res['original_draft']}")
                
            print(f"\nRetrieval Confidence: {res['retrieval_confidence']} (Top Sim: {res['retrieval_scores']['top_sim']:.2f})")
            print("Evidence:")
            for idx, ev in enumerate(res['evidence'], 1):
                print(f"  {idx}. {ev['case_id']} (Sim: {ev['similarity']:.2f})")
            print("--------------------------------------------------\n")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
