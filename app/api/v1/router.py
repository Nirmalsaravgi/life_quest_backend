"""
API v1 Router

Aggregates all v1 API routes.
"""

from fastapi import APIRouter

from app.api.v1 import auth, profiles, users

api_router = APIRouter()

# Include all route modules
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(profiles.router)

# Future routers will be added here:
# api_router.include_router(quests.router)
# api_router.include_router(skills.router)
# api_router.include_router(xp.router)
# api_router.include_router(streaks.router)
# api_router.include_router(powerups.router)
