from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parents[2] / "logs"
_FMT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
_DATE_FMT = "%Y-%m-%d %H:%M:%S"
_CONFIGURED = False


def _make_handler(filename: str) -> RotatingFileHandler:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(
        LOG_DIR / filename,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter(_FMT, datefmt=_DATE_FMT))
    return handler


def _attach(logger_names: tuple[str, ...], filename: str) -> None:
    handler = _make_handler(filename)
    for name in logger_names:
        lg = logging.getLogger(name)
        lg.setLevel(logging.INFO)
        if not any(isinstance(h, RotatingFileHandler) and h.baseFilename == handler.baseFilename for h in lg.handlers):
            lg.addHandler(handler)


def setup_logging() -> Path:
    """Konfigurasi file logging terpisah untuk app, ai, auth, dan worker."""
    global _CONFIGURED
    if _CONFIGURED:
        return LOG_DIR

    _attach(("app", "uvicorn.error", "uvicorn.access"), "app.log")
    _attach(("app.llm", "app.engine", "app.services.chat_service", "app.services.chat_context", "app.services.paraphrase_helper"), "ai.log")
    _attach(("app.api.v1.auth", "app.api.v1.auth_helpers", "app.api.v1.auth_password_reset", "app.services.auth_service", "app.services.upload_limits"), "auth.log")
    _attach(("app.workers", "celery"), "worker.log")

    _CONFIGURED = True
    logging.getLogger("app").info("Sistem file logging terpisah aktif di %s", LOG_DIR)
    return LOG_DIR
