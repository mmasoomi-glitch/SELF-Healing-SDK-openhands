import sys
import re

# Block edits to protected folders AND protected root files.
FORBIDDEN_TARGETS = [
    "vendor/",
    ".github/",
    "config/",
    "policies/",
    "standards/",
    "README.md",
    "AGENT_CONTRACT.md",
    "POLICY.md",
]

FORBIDDEN_PATTERNS = [
    r"subprocess",
    r"os\.system",
    r"eval\(",
    r"exec\(",
    r"curl",
    r"wget",
    r"ssh",
]

def check_patch(patch_text: str):
    for target in FORBIDDEN_TARGETS:
        if target in patch_text:
            return False, f"Modification of forbidden target: {target}"
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, patch_text):
            return False, f"Forbidden pattern detected: {pattern}"
    return True, "OK"

if __name__ == "__main__":
    patch = sys.stdin.read()
    ok, msg = check_patch(patch)
    if not ok:
        print(msg)
        sys.exit(1)
    print("Policy passed")
