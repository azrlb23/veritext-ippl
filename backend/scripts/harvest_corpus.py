from __future__ import annotations

import argparse
import hashlib
import sys
import time
import uuid
from functools import partial
from pathlib import Path

import httpx
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import settings
from app.engine.preprocessor import TextPreprocessor
from app.engine.tier1_lexical import WinnowingLexicalEngine
from app.engine.tier2_semantic import SemanticEngine
from app.models.corpus import CorpusDocument, DocumentChunk, LexicalFingerprint
from scripts.harvest_sources import fetch_arxiv_batch, fetch_doaj_batch, fetch_openalex_sliced

DOAJ_QUERIES = (
    "indonesia", "pendidikan", "kesehatan", "ekonomi", "hukum",
    "teknologi", "machine learning", "education", "public health", "computer science",
)
ARXIV_CATEGORIES = ("cs.AI", "cs.CL", "cs.LG", "cs.CV", "cs.SE", "stat.ML", "math.OC", "physics.soc-ph")
USER_AGENT = "VeriTextAI/1.0 (mailto:admin@veritext.ai)"


def flush_pending(session, lexical: WinnowingLexicalEngine, semantic: SemanticEngine, pending: list) -> int:
    if not pending:
        return 0
    all_sents = [s.text for _, _, sents in pending for s in sents]
    embs = semantic.embed_sentences(all_sents)
    emb_idx = 0
    for doc_row, abstract, sents in pending:
        session.add(doc_row)
        for idx, sent in enumerate(sents):
            session.add(DocumentChunk(
                corpus_doc_id=doc_row.id, chunk_index=idx,
                chunk_text=sent.text, embedding=embs[emb_idx],
            ))
            emb_idx += 1
        for h_val, pos in lexical.extract_fingerprints(abstract):
            session.add(LexicalFingerprint(corpus_doc_id=doc_row.id, fingerprint_hash=h_val, position_start=pos))
    session.commit()
    count = len(pending)
    pending.clear()
    return count


def queue_items(items: list[dict[str, str]], seen_hashes: set[str], pending: list, remaining_cap: int) -> None:
    for item in items:
        if remaining_cap <= 0:
            break
        title = item.get("title", "").strip()[:500]
        abstract = item.get("abstract", "").strip()
        if len(title) < 8 or len(abstract.split()) < 35:
            continue
        sha = hashlib.sha256(f"{title}\n{abstract}".encode()).hexdigest()
        if sha in seen_hashes:
            continue
        sents = [s for s in TextPreprocessor.segment_sentences(abstract) if s.word_count >= 5]
        if not sents:
            continue
        seen_hashes.add(sha)
        doc_id = uuid.uuid4()
        stored_name = f"{item['source_key']}_{str(doc_id)[:8]}"[:500]
        pending.append((
            CorpusDocument(
                id=doc_id, title=title, category=(item.get("category") or "Academic")[:255],
                academic_year=(item.get("year") or "")[:20], stored_filename=stored_name,
                sha256_hash=sha, status="INDEXED", total_chunks=len(sents),
            ),
            abstract, sents,
        ))
        remaining_cap -= 1


def harvest_groups(session, lexical, semantic, seen_hashes: set[str], groups, quota: int, tag: str) -> int:
    added, pending = 0, []
    for calls in groups:
        for label, fetch_fn in calls:
            if added + len(pending) >= quota:
                break
            try:
                items = fetch_fn()
            except Exception as err:  # noqa: BLE001
                print(f"[{tag}] {label} skipped: {err}", flush=True)
                time.sleep(0.2)
                continue
            if not items:
                break
            queue_items(items, seen_hashes, pending, quota - added - len(pending))
            if len(pending) >= 150:
                added += flush_pending(session, lexical, semantic, pending)
                print(f"[{tag}] {label} harvested={added}/{quota}", flush=True)
            time.sleep(0.2)
        if added + len(pending) >= quota:
            break
    added += flush_pending(session, lexical, semantic, pending)
    print(f"[{tag}] finished harvested={added}/{quota}", flush=True)
    return added


def main() -> None:
    parser = argparse.ArgumentParser(description="Harvest multi-source open-access academic corpus into pgvector")
    parser.add_argument("--target", type=int, default=15000, help="Total new documents to harvest in this run")
    parser.add_argument("--source", choices=["all", "openalex", "doaj", "arxiv"], default="all")
    parser.add_argument("--years", default="2025,2024,2023,2022,2021,2020", help="Comma-separated OpenAlex years")
    args = parser.parse_args()
    years = [y.strip() for y in args.years.split(",") if y.strip()]

    engine = create_engine(settings.DATABASE_URL.replace("+asyncpg", ""))
    Session = sessionmaker(bind=engine)
    lexical, semantic = WinnowingLexicalEngine(), SemanticEngine()

    with Session() as session, httpx.Client(timeout=30.0, headers={"User-Agent": USER_AGENT}) as client:
        seen_hashes = set(session.execute(text("SELECT sha256_hash FROM corpus_documents")).scalars().all())
        print(f"Existing corpus_documents={len(seen_hashes)}, target_new={args.target}, source={args.source}", flush=True)
        added = 0
        if args.source in ("all", "openalex"):
            q_id = args.target // 4 if args.source == "all" else args.target // 2
            oa_id = [[(f"y={y} p={p}", partial(fetch_openalex_sliced, client, "id", y, p)) for p in range(1, 51)] for y in years]
            added += harvest_groups(session, lexical, semantic, seen_hashes, oa_id, q_id, "OA-ID")
        if args.source in ("all", "doaj"):
            q_doaj = args.target // 4 if args.source == "all" else args.target
            doaj_g = [[(f"q={q} p={p}", partial(fetch_doaj_batch, client, q, p)) for p in range(1, 26)] for q in DOAJ_QUERIES]
            added += harvest_groups(session, lexical, semantic, seen_hashes, doaj_g, q_doaj, "DOAJ")
        if args.source in ("all", "arxiv"):
            q_arxiv = args.target // 4 if args.source == "all" else args.target
            arxiv_g = [[(f"cat={c} s={s}", partial(fetch_arxiv_batch, client, c, s)) for s in range(0, 2000, 200)] for c in ARXIV_CATEGORIES]
            added += harvest_groups(session, lexical, semantic, seen_hashes, arxiv_g, q_arxiv, "ARXIV")
        if args.source in ("all", "openalex") and added < args.target:
            oa_en = [[(f"y={y} p={p}", partial(fetch_openalex_sliced, client, "en", y, p)) for p in range(1, 51)] for y in years]
            added += harvest_groups(session, lexical, semantic, seen_hashes, oa_en, args.target - added, "OA-EN")
        total = session.execute(text("SELECT count(*) FROM corpus_documents")).scalar()
        print(f"DONE added_new={added} total_corpus_documents={total}", flush=True)


if __name__ == "__main__":
    main()
