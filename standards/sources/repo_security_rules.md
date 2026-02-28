# Repo Security Rules (Repo-Native)

Hard bans:
- subprocess, os.system, shell execution
- eval/exec
- curl/wget/ssh
- network usage (sandbox runs with --network=none)

Forbidden paths to modify:
- vendor/, .github/, config/, policies/, standards/
- README.md, AGENT_CONTRACT.md, POLICY.md

Secrets:
- Never commit tokens or keys.
- Never print environment secrets.
- Never embed credentials in code.
