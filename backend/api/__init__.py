"""
API 路由注册中心
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1")

from api.health import router as health_router
from api.auth import router as auth_router
from api.ask import router as ask_router
from api.symptoms import router as symptoms_router
from api.feedback import router as feedback_router
from api.history import router as history_router
from api.sync import router as sync_router
from api.transcribe import router as transcribe_router

router.include_router(health_router, tags=["System"])
router.include_router(auth_router, tags=["Auth"])
router.include_router(ask_router, tags=["Q&A"])
router.include_router(symptoms_router, tags=["Graph"])
router.include_router(feedback_router, tags=["Feedback"])
router.include_router(history_router, tags=["History"])
router.include_router(sync_router, tags=["Sync"])
router.include_router(transcribe_router, tags=["Tools"])
