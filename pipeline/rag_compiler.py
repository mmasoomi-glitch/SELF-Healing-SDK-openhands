import argparse
import hashlib
import json
import os
from datetime import datetime, timezone

MANIFEST = "standards/manifest.yaml"
CORPUS = "standards/compiled/rag_corpus.jsonl"

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()

def chunk_text(text: str, max_chars: int = 1200, overlap: int = 150):
    text = text.replace("\r\n", "\n")
    out = []
    i = 0
    while i < len(text):
        j = min(len(text), i + max_chars)
        chunk = text[i:j].strip()
        if chunk:
            out.append(chunk)
        i = max(j, i + max_chars - overlap)
    return out

def repo_inputs():
    roots = [
        "README.md",
        "AGENT_CONTRACT.md",
        "POLICY.md",
        "policies",
        "sandbox",
        "pipeline/task_schema.json",
        "pipeline/templates",
        "standards/sources",
        ".github/workflows",
        ".github/CODEOWNERS",
        "pyproject.toml",
        "package.json",
        "package-lock.json",
        "poetry.lock",
        "requirements.txt",
        "requirements.lock",
    ]
    files = []
    for r in roots:
        if os.path.isdir(r):
            for root, _, fs in os.walk(r):
                for fn in fs:
                    if fn.endswith((".md", ".py", ".json", ".yml", ".yaml", ".toml", ".txt")):
                        files.append(os.path.join(root, fn))
        elif os.path.isfile(r):
            files.append(r)
    return sorted(set(files))

def write_corpus(files):
    os.makedirs(os.path.dirname(CORPUS), exist_ok=True)
    h = hashlib.sha256()
    count = 0
    with open(CORPUS, "w", encoding="utf-8") as f:
        for path in files:
            text = read_text(path)
            fsha = hashlib.sha256(text.encode("utf-8")).hexdigest()
            for idx, chunk in enumerate(chunk_text(text)):
                obj = {
                    "id": f"{path}::chunk{idx}",
                    "source": path,
                    "source_sha256": fsha,
                    "chunk_index": idx,
                    "text": chunk,
                }
                line = json.dumps(obj, ensure_ascii=False)
                f.write(line + "\n")
                h.update((line + "\n").encode("utf-8"))
                count += 1
    return h.hexdigest(), count

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    files = repo_inputs()
    built_at = datetime.now(timezone.utc).isoformat()

    if args.write:
        corpus_sha, count = write_corpus(files)
        print(f"Wrote corpus: {CORPUS} chunks={count} sha256={corpus_sha}")
    else:
        print(f"DRY RUN inputs={len(files)}")

if __name__ == "__main__":
    main()
