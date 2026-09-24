# SupportProof Golden Set V1

This document freezes the definition of the SupportProof Golden Set Version 1.

* **Dataset Size:** 200 exactly
* **Domain:** AmazonHelp (Twitter Support)
* **Annotation Type:** 100% human-labelled
* **Taxonomy Version:** v0.1
* **Sampling Methodology:** Stratified deterministic heuristic sampling with strict deduplication (Seed: 42)
* **Escalation Annotation Methodology:** Conservative labeling; escalation implies required human intervention due to account/order specifics, repeated failure, or high frustration, not simply general dissatisfaction.
* **Date of Freeze:** September 2026

## IMPORTANT RESTRICTION
**This golden evaluation set is strictly held out from ALL training, tuning, or prompt-engineering feedback loops.**
It must only be used for final automated evaluation of the SupportProof agent and its classification/escalation models.
