from __future__ import annotations

import argparse
import hashlib
import sys
import uuid
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


def reconstruct_abstract(inv_idx: dict[str, list[int]] | None) -> str:
    if not inv_idx or not isinstance(inv_idx, dict):
        return ""
    max_pos = max((max(pos) for pos in inv_idx.values() if pos), default=-1)
    if max_pos < 0 or max_pos > 4000:
        return ""
    words = [""] * (max_pos + 1)
    for token, positions in inv_idx.items():
        for pos in positions:
            if 0 <= pos <= max_pos:
                words[pos] = token
    return " ".join(w for w in words if w).strip()


def fetch_openalex_batch(client: httpx.Client, lang: str, page: int) -> list[dict]:
    params = {
        "filter": f"has_abstract:true,language:{lang}",
        "per-page": 200,
        "page": page,
        "select": "id,title,publication_year,abstract_inverted_index,primary_topic",
    }
    resp = client.get("https://api.openalex.org/works", params=params)
    resp.raise_for_status()
    return resp.json().get("results", [])


def harvest_language(
    session, lexical: WinnowingLexicalEngine, semantic: SemanticEngine,
    seen_hashes: set[str], lang: str, quota: int,
) -> int:
    added, page = 0, 1
    with httpx.Client(timeout=30.0, headers={"User-Agent": "VeriTextAI/1.0 (mailto:admin@veritext.ai)"}) as client:
        while added < quota and page <= 50:
            try:
                works = fetch_openalex_batch(client, lang, page)
            except Exception as err:  # noqa: BLE001
                print(f"[{lang.upper()}] page={page} skipped: {err}", flush=True)
                page += 1
                continue
            page += 1
            if not works:
                break
            pending_docs, all_sents = [], []
            for w in works:
                if added + len(pending_docs) >= quota:
                    break
                title = " ".join(str(w.get("title") or "").split())[:490]
                abstract = reconstruct_abstract(w.get("abstract_inverted_index"))
                if len(title) < 8 or len(abstract.split()) < 35:
                    continue
                sha = hashlib.sha256(f"{title}\n{abstract}".encode()).hexdigest()
                if sha in seen_hashes:
                    continue
                seen_hashes.add(sha)
                sents = [s for s in TextPreprocessor.segment_sentences(abstract) if s.word_count >= 5]
                if not sents:
                    continue
                cat = ((w.get("primary_topic") or {}).get("display_name") or f"OpenAlex ({lang.upper()})")[:250]
                doc_id = uuid.uuid4()
                oa_id = str(w.get("id") or doc_id).rsplit("/", 1)[-1]
                pending_docs.append((
                    CorpusDocument(
                        id=doc_id, title=title, category=cat,
                        academic_year=str(w.get("publication_year") or ""),
                        stored_filename=f"oa_{lang}_{oa_id}_{str(doc_id)[:8]}",
                        sha256_hash=sha, status="INDEXED", total_chunks=len(sents),
                    ),
                    abstract,
                    sents,
                ))
                all_sents.extend(s.text for s in sents)

            if not pending_docs:
                continue
            embs = semantic.embed_sentences(all_sents)
            emb_idx = 0
            for doc_row, abstract, sents in pending_docs:
                session.add(doc_row)
                for idx, s in enumerate(sents):
                    session.add(DocumentChunk(
                        corpus_doc_id=doc_row.id, chunk_index=idx,
                        chunk_text=s.text, embedding=embs[emb_idx],
                    ))
                    emb_idx += 1
                for h_val, pos in lexical.extract_fingerprints(abstract):
                    session.add(LexicalFingerprint(
                        corpus_doc_id=doc_row.id, fingerprint_hash=h_val, position_start=pos,
                    ))
            session.commit()
            added += len(pending_docs)
            print(f"[{lang.upper()}] harvested={added}/{quota}", flush=True)
    return added


def main() -> None:
    parser = argparse.ArgumentParser(description="Harvest open-access academic corpus from OpenAlex into pgvector")
    parser.add_argument("--target", type=int, default=10000, help="Total new documents to harvest (50% ID, 50% EN)")
    args = parser.parse_args()

    sync_url = settings.DATABASE_URL.replace("+asyncpg", "")
    engine = create_engine(sync_url)
    Session = sessionmaker(bind=engine)
    lexical = WinnowingLexicalEngine()
    semantic = SemanticEngine()

    with Session() as session:
        existing = session.execute(text("SELECT sha256_hash FROM corpus_documents")).scalars().all()
        seen_hashes = set(existing)
        print(f"Existing corpus_documents={len(seen_hashes)}, target_new={args.target}", flush=True)
        half = args.target // 2
        n_id = harvest_language(session, lexical, semantic, seen_hashes, "id", half)
        n_en = harvest_language(session, lexical, semantic, seen_hashes, "en", args.target - n_id)
        total = session.execute(text("SELECT count(*) FROM corpus_documents")).scalar()
        print(f"DONE added_id={n_id} added_en={n_en} total_corpus_documents={total}", flush=True)


if __name__ == "__main__":
    main()
