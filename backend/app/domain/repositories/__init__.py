"""
Repository Interfaces (Domain Layer)
Abstract protocols defining data access contracts
"""

from app.domain.repositories.user_repository import IUserRepository

__all__ = ["IUserRepository"]
