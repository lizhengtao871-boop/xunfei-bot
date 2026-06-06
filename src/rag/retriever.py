import json
import math
import hashlib
from pathlib import Path
from collections import defaultdict
import jieba
from src.config import config
from src.rag.loader import load_all_documents
from src.rag.splitter import split_documents

_INDEX_PATH = Path(config.CHROMA_PERSIST_DIR) / "kb_index.json"
_chunks: list[dict] = []
_doc_freq: dict[str, int] = {}
_avg_doc_len: float = 0


def _tokenize(text: str) -> list[str]:
    return [w.strip() for w in jieba.cut(text) if w.strip() and len(w.strip()) > 1]


def _content_hash(content: str) -> str:
    return hashlib.md5(content.encode("utf-8")).hexdigest()


def build_knowledge_base(docs_dir: str | None = None):
    global _chunks, _doc_freq, _avg_doc_len

    docs_dir = docs_dir or config.DOCS_DIR
    docs = load_all_documents(docs_dir)
    if not docs:
        print("No documents found in", docs_dir)
        return

    new_chunks = split_documents(docs)

    # Load existing index to avoid duplicates
    existing_hashes = {_content_hash(c["content"]) for c in _chunks}
    for chunk in new_chunks:
        if _content_hash(chunk["content"]) not in existing_hashes:
            _chunks.append(chunk)
            existing_hashes.add(_content_hash(chunk["content"]))

    # Rebuild token frequency index
    _doc_freq = defaultdict(int)
    total_words = 0
    for chunk in _chunks:
        tokens = set(_tokenize(chunk["content"]))
        for t in tokens:
            _doc_freq[t] += 1
        total_words += len(tokens)

    _avg_doc_len = total_words / max(len(_chunks), 1)

    # Persist to disk
    _INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    _INDEX_PATH.write_text(json.dumps(_chunks, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Knowledge base built: {len(_chunks)} chunks indexed.")


def _load_index():
    global _chunks, _doc_freq, _avg_doc_len
    if _chunks:
        return
    if _INDEX_PATH.exists():
        _chunks = json.loads(_INDEX_PATH.read_text(encoding="utf-8"))
        _doc_freq = defaultdict(int)
        total_words = 0
        for chunk in _chunks:
            tokens = set(_tokenize(chunk["content"]))
            for t in tokens:
                _doc_freq[t] += 1
            total_words += len(tokens)
        _avg_doc_len = total_words / max(len(_chunks), 1)


def search(query: str, top_k: int = 5) -> list[dict]:
    _load_index()
    if not _chunks:
        return []

    query_tokens = _tokenize(query)
    if not query_tokens:
        return []

    N = len(_chunks)
    k1, b = 1.5, 0.75

    # Pre-tokenize all docs
    doc_tokens_list = [_tokenize(c["content"]) for c in _chunks]
    doc_lens = [len(tokens) for tokens in doc_tokens_list]

    scores = []
    for i, doc_tokens in enumerate(doc_tokens_list):
        score = 0.0
        term_freqs = defaultdict(int)
        for t in doc_tokens:
            term_freqs[t] += 1

        for qt in query_tokens:
            tf = term_freqs.get(qt, 0)
            if tf == 0:
                continue
            df = _doc_freq.get(qt, 0)
            idf = math.log((N - df + 0.5) / (df + 0.5) + 1.0)
            doc_len_norm = 1 - b + b * (doc_lens[i] / _avg_doc_len) if _avg_doc_len > 0 else 1
            score += idf * (tf * (k1 + 1)) / (tf + k1 * doc_len_norm)

        if score > 0:
            scores.append((i, score))

    scores.sort(key=lambda x: x[1], reverse=True)

    # Normalize scores to 0-1 range
    max_score = scores[0][1] if scores else 1
    return [
        {
            "content": _chunks[i]["content"],
            "source": _chunks[i].get("source", ""),
            "score": round(score / max_score, 4) if max_score > 0 else 0,
        }
        for i, score in scores[:top_k]
    ]
