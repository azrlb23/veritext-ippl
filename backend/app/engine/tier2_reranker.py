from __future__ import annotations

import logging

from app.core.config import settings
from app.engine.language_detector import detect_language
from app.engine.tier2_en_reranker import EnglishReranker
from app.engine.tier2_indobert import IndoBertScorer

logger = logging.getLogger(__name__)


class SemanticReranker:
    """Re-ranker Tier 2 dua lapis: cross-encoder (antonim ditolak), lalu ambang bawah IndoBERT (pasangan tak berkaitan ditolak)."""

    _model = None
    _attempted = False

    @classmethod
    def get_model(cls):
        if not settings.RERANKER_ENABLED:
            return None
        if not cls._attempted:
            cls._attempted = True
            try:
                from sentence_transformers import CrossEncoder

                cls._model = CrossEncoder(settings.RERANKER_MODEL, max_length=512)
            except Exception as err:  # noqa: BLE001
                logger.warning("Re-ranker tidak dapat dimuat, memakai skor MiniLM saja: %s", err)
                cls._model = None
        return cls._model

    @classmethod
    def score_pairs(cls, pairs: list[tuple[str, str]]) -> list[float] | None:
        model = cls.get_model()
        if model is None or not pairs:
            return None
        try:
            return [float(x) for x in model.predict(pairs, batch_size=16)]
        except Exception as err:  # noqa: BLE001
            logger.warning("Re-ranker gagal menilai pasangan, memakai skor MiniLM saja: %s", err)
            return None

    @classmethod
    def accept_mask(
        cls,
        pairs: list[tuple[str, str]],
        similarities: list[float] | None = None,
    ) -> list[bool]:
        scores = cls.score_pairs(pairs)
        cross = [True] * len(pairs) if scores is None else [s >= settings.RERANKER_THRESHOLD for s in scores]
        survivor_indices = [i for i, ok in enumerate(cross) if ok]
        if not survivor_indices:
            return cross

        id_idx: list[int] = []
        en_idx: list[int] = []
        cross_lang_idx: list[int] = []
        for i in survivor_indices:
            lang_a = detect_language(pairs[i][0])
            lang_b = detect_language(pairs[i][1])
            if lang_a == "id" and lang_b == "id":
                id_idx.append(i)
            elif lang_a == "en" and lang_b == "en":
                en_idx.append(i)
            else:
                cross_lang_idx.append(i)

        id_mask = IndoBertScorer.accept_mask([pairs[i] for i in id_idx]) if id_idx else []
        en_mask = EnglishReranker.accept_mask([pairs[i] for i in en_idx]) if en_idx else []

        final = list(cross)
        for idx, ok in zip(id_idx, id_mask):
            final[idx] = ok
        for idx, ok in zip(en_idx, en_mask):
            final[idx] = ok
        for idx in cross_lang_idx:
            final[idx] = cross[idx] and (similarities is None or similarities[idx] >= 0.80)
        return final
