from __future__ import annotations

import logging

from app.core.config import settings
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
    def accept_mask(cls, pairs: list[tuple[str, str]]) -> list[bool]:
        scores = cls.score_pairs(pairs)
        cross = [True] * len(pairs) if scores is None else [s >= settings.RERANKER_THRESHOLD for s in scores]
        survivors = [pair for pair, ok in zip(pairs, cross) if ok]
        floor = iter(IndoBertScorer.accept_mask(survivors))
        return [ok and next(floor) for ok in cross]
