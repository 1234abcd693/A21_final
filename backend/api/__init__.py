from fastapi import APIRouter

router = APIRouter(prefix="/api/v1")

# 各模块路由在此注册（Agent 开发时逐步添加）
# from api.ask import router as ask_router      → router.include_router(ask_router)
# from api.symptoms import router as sym_router → router.include_router(sym_router)
# from api.graph import router as graph_router  → router.include_router(graph_router)
# ...
