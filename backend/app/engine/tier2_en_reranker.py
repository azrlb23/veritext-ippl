from __future__ import annotations

import logging

logger = logging.getLogger(__name__)
EN_RERANKER_MODEL = "cross-encoder/stsb-distilroberta-base"
EN_RERANKER_MIN_SIM = 0.45


class EnglishReranker:
    """Re-ranker STS-B khusus bahasa Inggris dari Hugging Face (fail-open jika tidak tersedia)."""

    _model = None
    _attempted = False

    @classmethod
    def get_model(cls):
        if not cls._attempted:
            cls._attempted = True
            try:
                from sentence_transformers import CrossEncoder

                cls._model = CrossEncoder(EN_RERANKER_MODEL, max_length=512)
            except Exception as err:  # noqa: BLE001
                logger.warning("English reranker tidak dapat dimuat, memakai skor BGE-M3 saja: %s", err)
                cls._model = None
        return cls._model

    @classmethod
    def accept_mask(cls, pairs: list[tuple[str, str]]) -> list[bool]:
        if not pairs:
            return []
        model = cls.get_model()
        if model is None:
            return [True] * len(pairs)
        try:
            scores = [float(x) for x in model.predict(pairs, batch_size=16)]
            return [s >= EN_RERANKER_MIN_SIM for s in scores]
        except Exception as err:  # noqa: BLE001
            logger.warning("English reranker gagal menilai pasangan: %s", err)
            return [True] * len(pairs)
