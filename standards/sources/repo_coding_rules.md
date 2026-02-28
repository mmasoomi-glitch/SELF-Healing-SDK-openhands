# Repo Coding Rules (Repo-Native)

- Agent may write only in modules/ and logs/.
- Every change must include unit tests.
- Output must include: plan.json + patch.diff + grounding.json.
- Keep diffs minimal. No unrelated refactors.
- Prefer standard library. Avoid new dependencies.
- No global mutable state.
- Explicit return types where reasonable.
- Clear, readable function names.
