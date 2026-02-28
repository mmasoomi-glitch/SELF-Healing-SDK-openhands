import json
import sys

REQUIRED_SOURCES = [
    "AGENT_CONTRACT.md",
    "POLICY.md",
]

def main():
    if len(sys.argv) < 3:
        print("Usage: python policies/grounding_validator.py <grounding.json> <corpus.jsonl>")
        sys.exit(2)

    grounding_path = sys.argv[1]
    corpus_path = sys.argv[2]

    g = json.load(open(grounding_path, "r", encoding="utf-8"))
    retrieval = g.get("retrieval", {})
    cited_ids = retrieval.get("cited_chunk_ids", [])
    query = retrieval.get("query", "")

    if not isinstance(query, str) or len(query.strip()) < 5:
        print("FAIL: retrieval.query missing/too short")
        sys.exit(1)

    min_required = int(retrieval.get("min_required", 3))
    if not isinstance(cited_ids, list) or len(cited_ids) < min_required:
        print("FAIL: insufficient cited_chunk_ids")
        sys.exit(1)

    id_to_source = {}
    with open(corpus_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            cid = obj.get("id")
            src = obj.get("source")
            if cid and src:
                id_to_source[cid] = src

    missing = [cid for cid in cited_ids if cid not in id_to_source]
    if missing:
        print("FAIL: cited ids not found in corpus:", missing[:10])
        sys.exit(1)

    cited_sources = {id_to_source[cid] for cid in cited_ids}

    for req in REQUIRED_SOURCES:
        if req not in cited_sources:
            print(f"FAIL: grounding must cite at least one chunk from {req}")
            sys.exit(1)

    print("PASS: grounding validator ok")
    sys.exit(0)

if __name__ == "__main__":
    main()
