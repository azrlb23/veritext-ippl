from __future__ import annotations

import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class SemanticReranker:
    """Cross-encoder yang menilai ulang kandidat Tier 2 agar pasangan berlawanan makna tidak lolos."""

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
        if scores is None:
            return [True] * len(pairs)
        return [s >= settings.RERANKER_THRESHOLD for s in scores]
