from types import SimpleNamespace
import pytest

from app.engine.reference_corpus import BUILTIN_REFERENCE_CORPUS
from app.services.source_preview_service import build_source_preview


class _EmptyResult:
    def scalar_one_or_none(self):
        return None

    def scalars(self):
        return self

    def all(self):
        return []


class _FakeDb:
    async def execute(self, _stmt):
        return _EmptyResult()


@pytest.mark.asyncio
async def test_build_source_preview_returns_builtin_corpus_full_text():
    doc = BUILTIN_REFERENCE_CORPUS[0]
    report = SimpleNamespace(
        heatmap_annotations=[
            {
                "tier": "T1",
                "source_title": doc["title"],
                "text_snippet": "Kalimat uji dari naskah.",
                "matched_source_text": doc["text"][:100],
                "similarity": 0.92,
            }
        ]
    )
    res = await build_source_preview(_FakeDb(), report, title=doc["title"], corpus_doc_id=str(doc["id"]))
    assert res["source_type"] == "corpus"
    assert res["full_text"] == doc["text"]
    assert len(res["matched_highlights"]) == 1


@pytest.mark.asyncio
async def test_build_source_preview_collects_web_snippets_when_offline():
    report = SimpleNamespace(
        heatmap_annotations=[
            {
                "tier": "T2",
                "source_title": "Jurnal Uji",
                "source_url": None,
                "text_snippet": "Kalimat naskah satu.",
                "matched_source_text": "Kutipan dari jurnal uji.",
                "similarity": 0.85,
            }
        ]
    )
    res = await build_source_preview(_FakeDb(), report, title="Jurnal Uji")
    assert "Kutipan dari jurnal uji." in res["full_text"]
    assert len(res["matched_highlights"]) == 1
