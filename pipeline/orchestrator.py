import json
import os
import subprocess
from typing import Dict, Any, List

from pipeline.retriever import retrieve
from sandbox.runner import run_module

CORPUS_PATH = "standards/compiled/rag_corpus.jsonl"


def run_cmd(cmd: List[str], input_text: str = "") -> subprocess.CompletedProcess:
    return subprocess.run(cmd, input=input_text, text=True, capture_output=True)


def extract_module_names_from_patch(patch_text: str) -> List[str]:
    names = set()
    for line in patch_text.splitlines():
        if line.startswith("+++ b/modules/") or line.startswith("--- a/modules/"):
            rest = line.split("modules/", 1)[1]
            mod = rest.split("/", 1)[0].strip()
            if mod:
                names.add(mod)
    return sorted(names)


def model_call_stub(prompt: str) -> Dict[str, Any]:
    # MODEL_CALL_NOT_IMPLEMENTED
    # Replace this with your actual LLM API call.
    # Must return: {"plan_json": str, "patch_diff": str, "grounding_json": str}
    raise RuntimeError("MODEL_CALL_NOT_IMPLEMENTED")


def main(task_path: str):
    # Step 1: Refresh grounding corpus
    subprocess.check_call(["python", "pipeline/rag_compiler.py", "--write"])

    # Step 2: Load task
    task = json.load(open(task_path, "r", encoding="utf-8"))
    goal = task.get("goal", "")
    constraints = task.get("constraints", [])
    query = " ".join([goal] + constraints)

    # Step 3: Retrieve grounding evidence
    hits = retrieve(query, top_k=8)
    cited_ids = [h.id for h in hits]

    if len(cited_ids) < 3:
        raise RuntimeError("INSUFFICIENT_RETRIEVAL: stop to avoid hallucination")

    grounding_block = "\n\n".join([f"[{h.id}] {h.text}" for h in hits])

    prompt = f"""You are an untrusted coding agent.
Follow AGENT_CONTRACT.md and POLICY.md.

You MUST output:
- plan_json (JSON)
- patch_diff (unified diff)
- grounding_json (JSON) with cited_chunk_ids from this list only: {cited_ids}

TASK:
{json.dumps(task, indent=2)}

RETRIEVED GROUNDS:
{grounding_block}
"""

    # Step 4: Bounded retry loop (max 3 per AGENT_CONTRACT.md)
    max_iter = 3
    last_error = ""

    for attempt in range(1, max_iter + 1):
        out = model_call_stub(prompt + (f"\n\nPREVIOUS_ERROR:\n{last_error}" if last_error else ""))

        plan_json = out["plan_json"]
        patch_diff = out["patch_diff"]
        grounding_json = out["grounding_json"]

        os.makedirs("logs", exist_ok=True)
        open("logs/plan.json", "w", encoding="utf-8").write(plan_json)
        open("logs/patch.diff", "w", encoding="utf-8").write(patch_diff)
        open("logs/grounding.json", "w", encoding="utf-8").write(grounding_json)

        # Gate 1: Policy enforcer (patch scan)
        p = run_cmd(["python", "policies/enforcer.py"], input_text=patch_diff)
        if p.returncode != 0:
            last_error = "POLICY_ENFORCER_FAIL: " + (p.stdout + p.stderr)
            continue

        # Gate 2: Grounding required (IDs exist)
        g1 = subprocess.run(
            ["python", "policies/grounding_required.py", "logs/grounding.json"],
            capture_output=True, text=True
        )
        if g1.returncode != 0:
            last_error = "GROUNDING_REQUIRED_FAIL: " + (g1.stdout + g1.stderr)
            continue

        # Gate 3: Grounding validator (must cite contract + policy)
        g2 = subprocess.run(
            ["python", "policies/grounding_validator.py", "logs/grounding.json", CORPUS_PATH],
            capture_output=True, text=True
        )
        if g2.returncode != 0:
            last_error = "GROUNDING_VALIDATOR_FAIL: " + (g2.stdout + g2.stderr)
            continue

        # Gate 4: Apply patch safely
        chk = run_cmd(["git", "apply", "--check", "-"], input_text=patch_diff)
        if chk.returncode != 0:
            last_error = "GIT_APPLY_CHECK_FAIL: " + (chk.stdout + chk.stderr)
            continue

        ap = run_cmd(["git", "apply", "-"], input_text=patch_diff)
        if ap.returncode != 0:
            last_error = "GIT_APPLY_FAIL: " + (ap.stdout + ap.stderr)
            continue

        # Gate 5: Sandbox test
        mods = extract_module_names_from_patch(patch_diff)
        if not mods:
            last_error = "NO_MODULE_TOUCHED: patch must modify modules/<name>/"
            continue

        for m in mods:
            code, out_s, err_s = run_module(m)
            if code != 0:
                last_error = f"SANDBOX_FAIL module={m}\n{out_s}\n{err_s}"
                break
        else:
            print("SUCCESS: all gates passed")
            return

    raise RuntimeError("FAILURE: max iterations exceeded. Last error: " + last_error)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python pipeline/orchestrator.py <task.json>")
        raise SystemExit(2)
    main(sys.argv[1])
