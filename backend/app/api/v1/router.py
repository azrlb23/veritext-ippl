from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.documents import router as documents_router
from app.api.v1.audits import router as audits_router
from app.api.v1.reports import router as reports_router
from app.api.v1.corpus import router as corpus_router
from app.api.v1.billing import router as billing_router
from app.api.v1.admin import router as admin_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(auth_router)
api_v1_router.include_router(documents_router)
api_v1_router.include_router(audits_router)
api_v1_router.include_router(reports_router)
api_v1_router.include_router(corpus_router)
api_v1_router.include_router(billing_router)
api_v1_router.include_router(admin_router)
