# POLICY

This repository enforces machine-level policy on all agent output.

Enforcement layers:
1. AGENT_CONTRACT.md - Root law.
2. policies/enforcer.py - Non-LLM policy check.
3. policies/grounding_required.py - Rejects output without grounding evidence.
4. sandbox/runner.py - Docker execution: CPU/memory limits, no network, read-only mount.
5. GitHub branch protection - No direct push to main.

Violation handling:
- Policy violation -> patch rejected
- Missing tests -> rejected
- Missing grounding evidence -> rejected
- Forbidden path touched -> rejected
- Max iterations exceeded -> FAILURE
