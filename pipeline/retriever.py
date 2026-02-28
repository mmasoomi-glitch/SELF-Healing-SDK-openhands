import json
import re
from dataclasses import dataclass
from typing import List, Dict, Tuple

CORPUS_PATH = "standards/compiled/rag_corpus.jsonl"

def _tokenize(text: str) -> List[str]:
    text = text.lower()
    return re.findall(r"[a-z0-9_./-]{2,}", text)

@dataclass
class RetrievalResult:
    id: str
    source: str
    score: float
    text: str

def load_corpus() -> List[Dict]:
    items: List[Dict] = []
    with open(CORPUS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            items.append(json.loads(line))
    return items

def retrieve(query: str, top_k: int = 8) -> List[RetrievalResult]:
    q_toks = _tokenize(query)
    if not q_toks:
        return []

    q_set = set(q_toks)
    corpus = load_corpus()

    scored: List[Tuple[float, Dict]] = []
    for item in corpus:
        t_toks = _tokenize(item.get("text", ""))
        if not t_toks:
            continue
        t_set = set(t_toks)
        inter = len(q_set & t_set)
        union = len(q_set | t_set)
        score = inter / (union + 1e-9)
        if score > 0:
            scored.append((score, item))

    scored.sort(key=lambda x: x[0], reverse=True)

    out: List[RetrievalResult] = []
    for score, item in scored[:top_k]:
        out.append(RetrievalResult(
            id=item["id"],
            source=item["source"],
            score=float(score),
            text=item["text"],
        ))
    return out
