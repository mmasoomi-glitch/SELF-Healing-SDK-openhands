import json
import os
import sys

CORPUS_PATH = "standards/compiled/rag_corpus.jsonl"

def load_ids():
    ids = set()
    if not os.path.isfile(CORPUS_PATH):
        return ids
    with open(CORPUS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            ids.add(obj.get("id"))
    return ids

def main():
    if len(sys.argv) < 2:
        print("Usage: python policies/grounding_required.py grounding.json")
        sys.exit(2)

    path = sys.argv[1]

    if not os.path.isfile(path):
        print("FAIL: grounding.json missing")
        sys.exit(1)

    data = json.load(open(path, "r", encoding="utf-8"))
    cited = data.get("retrieval", {}).get("cited_chunk_ids", [])

    if not cited:
        print("FAIL: no grounding evidence")
        sys.exit(1)

    corpus_ids = load_ids()

    if not corpus_ids:
        print("FAIL: corpus missing")
        sys.exit(1)

    missing = [x for x in cited if x not in corpus_ids]

    if missing:
        print("FAIL: invalid grounding ids:", missing[:10])
        sys.exit(1)

    print("PASS: grounding valid")

if __name__ == "__main__":
    main()
