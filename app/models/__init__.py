"""
SQLAlchemy Models Package

Exports all models for easy importing and Alembic discovery.
"""

# User & Authentication
from app.models.user import AuthProvider, User, UserSession

# Profile & Identity
from app.models.profile import Archetype, LifeMode, UserProfile

# Life Areas
from app.models.life_area import LifeArea, UserLifeArea

# Skills
from app.models.skill import Skill, SkillPrerequisite, SkillTree, UserSkill

# Quests
from app.models.quest import Quest, QuestCompletion, QuestType

# XP
from app.models.xp import UserXP, XPDecayLog

# Streaks
from app.models.streak import Streak

# Power-ups
from app.models.powerup import ActivePowerUp, PowerUp, UserInventory

# Titles
from app.models.title import Title, UserTitle

__all__ = [
    # User & Auth
    "User",
    "AuthProvider",
    "UserSession",
    # Profile
    "Archetype",
    "LifeMode",
    "UserProfile",
    # Life Areas
    "LifeArea",
    "UserLifeArea",
    # Skills
    "SkillTree",
    "Skill",
    "SkillPrerequisite",
    "UserSkill",
    # Quests
    "QuestType",
    "Quest",
    "QuestCompletion",
    # XP
    "UserXP",
    "XPDecayLog",
    # Streaks
    "Streak",
    # Power-ups
    "PowerUp",
    "UserInventory",
    "ActivePowerUp",
    # Titles
    "Title",
    "UserTitle",
]
