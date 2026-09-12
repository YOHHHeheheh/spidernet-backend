from fastapi import APIRouter
from app.api.v1.endpoints import auth, search, analytics, live_feed

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(search.router, prefix="/graph", tags=["Graph Traversal"])
api_router.include_router(analytics.router, prefix="/graph", tags=["Graph Analytics"])
api_router.include_router(live_feed.router, prefix="/ws", tags=["Live Telemetry"])
