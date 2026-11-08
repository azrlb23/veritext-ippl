from __future__ import annotations

import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class IndoBertScorer:
    """Kemiripan kosinus embedding IndoBERT (768-d) sebagai lapis kedua re-ranking Tier 2.

    Bi-encoder tidak dapat membedakan pasangan berlawanan makna (kosinusnya tetap tinggi), jadi lapis ini hanya
    berfungsi sebagai ambang bawah: pasangan yang kosinusnya rendah ditolak meski cross-encoder meloloskannya.
    """

    _model = None
    _attempted = False

    @classmethod
    def get_model(cls):
        if not settings.INDOBERT_ENABLED:
            return None
        if not cls._attempted:
            cls._attempted = True
            try:
                from sentence_transformers import SentenceTransformer

                cls._model = SentenceTransformer(settings.INDOBERT_MODEL)
            except Exception as err:  # noqa: BLE001
                logger.warning("IndoBERT tidak dapat dimuat, re-ranking hanya memakai cross-encoder: %s", err)
                cls._model = None
        return cls._model

    @classmethod
    def similarities(cls, pairs: list[tuple[str, str]]) -> list[float] | None:
        model = cls.get_model()
        if model is None or not pairs:
            return None
        try:
            left = model.encode([a for a, _ in pairs], batch_size=16, normalize_embeddings=True)
            right = model.encode([b for _, b in pairs], batch_size=16, normalize_embeddings=True)
            return [float((l_vec * r_vec).sum()) for l_vec, r_vec in zip(left, right)]
        except Exception as err:  # noqa: BLE001
            logger.warning("IndoBERT gagal menilai pasangan: %s", err)
            return None

    @classmethod
    def accept_mask(cls, pairs: list[tuple[str, str]]) -> list[bool]:
        sims = cls.similarities(pairs)
        if sims is None:
            return [True] * len(pairs)
        return [s >= settings.INDOBERT_MIN_SIM for s in sims]
