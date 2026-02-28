# AGENT CONTRACT (MANDATORY)

The agent is untrusted.

The agent MUST obey the following:

1. Allowed write locations:
   - modules/
   - logs/

2. Forbidden modifications:
   - vendor/
   - .github/
   - config/
   - policies/
   - standards/
   - README.md
   - AGENT_CONTRACT.md
   - POLICY.md

3. The agent MUST output:
   - A JSON plan
   - A unified diff patch
   - Unit tests
   - A grounding.json file with retrieved evidence

4. The agent MUST NOT:
   - Use network
   - Install packages unless explicitly allowed
   - Use subprocess
   - Use shell execution
   - Use eval/exec
   - Modify CI or workflows
   - Modify security configuration

5. Maximum 3 debug iterations.

6. If uncertain -> STOP and return FAILURE.

Violation of contract = rejection.
