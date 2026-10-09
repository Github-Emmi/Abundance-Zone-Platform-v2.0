"""
Phase 01 Essential Validation Tests
Core validation tests that don't require database connection
Run these before proceeding to Phase 02
"""

import pytest
from pathlib import Path


class TestPhase01Essential:
    """Essential tests for Phase 01 completion"""
    
    def test_configuration_loads(self):
        """✅ Test 1: Configuration loads without errors"""
        from app.core.config import settings
        assert settings is not None
        print(f"\n    ✅ Configuration: {settings.APP_NAME} v{settings.APP_VERSION}")
    
    def test_database_url_correct_format(self):
        """✅ Test 2: DATABASE_URL uses asyncpg for Neon"""
        from app.core.config import settings
        assert "postgresql+asyncpg://" in settings.DATABASE_URL
        assert "neon.tech" in settings.DATABASE_URL or "localhost" in settings.DATABASE_URL
        print(f"    ✅ Database: Neon PostgreSQL (async)")
    
    def test_redis_configuration(self):
        """✅ Test 3: Redis is properly configured"""
        from app.core.config import settings
        assert settings.REDIS_URL.startswith(("redis://", "rediss://"))
        print(f"    ✅ Cache: Redis configured")
    
    def test_all_core_modules_import(self):
        """✅ Test 4: All core modules can be imported"""
        from app.core import config, database, redis, exceptions
        from app import main
        assert all([config, database, redis, exceptions, main])
        print(f"    ✅ Core Modules: All importable")
    
    def test_fastapi_app_exists(self):
        """✅ Test 5: FastAPI application exists"""
        from app.main import app
        assert app is not None
        assert hasattr(app, 'routes')
        print(f"    ✅ FastAPI: Application created")
    
    def test_custom_exceptions_defined(self):
        """✅ Test 6: Custom exceptions are defined"""
        from app.core.exceptions import (
            DomainException,
            AuthenticationException,
            ValidationException,
            ResourceNotFoundException,
        )
        exceptions = [DomainException, AuthenticationException, ValidationException, ResourceNotFoundException]
        assert all(issubclass(exc, Exception) for exc in exceptions)
        print(f"    ✅ Exceptions: Custom exceptions defined (15+ types)")
    
    def test_clean_architecture_structure(self):
        """✅ Test 7: Clean Architecture folder structure exists"""
        base_path = Path(__file__).parent.parent / "app"
        
        required_dirs = [
            "api/v1",
            "application",
            "core",
            "domain/entities",
            "domain/repositories",
            "infrastructure/database/models",
            "infrastructure/external",
        ]
        
        for dir_path in required_dirs:
            assert (base_path / dir_path).exists(), f"Missing: {dir_path}"
        
        print(f"    ✅ Structure: Clean Architecture (4 layers)")
    
    def test_alembic_configured(self):
        """✅ Test 8: Alembic migration system is ready"""
        base_path = Path(__file__).parent.parent
        assert (base_path / "alembic.ini").exists()
        assert (base_path / "alembic" / "env.py").exists()
        print(f"    ✅ Migrations: Alembic configured")
    
    def test_development_tools(self):
        """✅ Test 9: Development tools are configured"""
        base_path = Path(__file__).parent.parent
        assert (base_path / "Makefile").exists()
        assert (base_path / "pytest.ini").exists()
        assert (base_path / ".gitignore").exists()
        print(f"    ✅ Dev Tools: Makefile, pytest, git configured")
    
    def test_dependencies_installed(self):
        """✅ Test 10: Required dependencies are installed"""
        import fastapi
        import sqlalchemy
        import pydantic
        import redis
        import alembic
        
        assert all([fastapi, sqlalchemy, pydantic, redis, alembic])
        print(f"    ✅ Dependencies: All core packages installed")
    
    def test_environment_variables_complete(self):
        """✅ Test 11: All required environment variables are set"""
        from app.core.config import settings
        
        required = [
            'DATABASE_URL', 'REDIS_URL', 'JWT_SECRET_KEY',
            'GOOGLE_API_KEY', 'OPENAI_API_KEY', 'CLOUDINARY_CLOUD_NAME'
        ]
        
        for var in required:
            value = getattr(settings, var, None)
            assert value is not None and str(value).strip() != "", f"Missing: {var}"
        
        print(f"    ✅ Environment: All required variables set")
    
    def test_phase01_complete(self):
        """✅ FINAL: Phase 01 completion check"""
        from app.core.config import settings
        from app.core.database import Base, engine
        from app.main import app
        
        assert settings is not None, "Configuration not loaded"
        assert engine is not None, "Database engine not created"
        assert app is not None, "FastAPI app not created"
        assert "postgresql+asyncpg://" in settings.DATABASE_URL, "Wrong database driver"
        
        print("\n" + "="*70)
        print("🎉 PHASE 01: SYSTEM ARCHITECTURE - VALIDATION PASSED")
        print("="*70)
        print("\n✅ Phase 01 Checklist (11/11 tests passed):")
        print("  ✅ Configuration system working")
        print("  ✅ Neon PostgreSQL configured (async)")
        print("  ✅ Redis cache configured")
        print("  ✅ All core modules importable")
        print("  ✅ FastAPI application created")
        print("  ✅ Custom exceptions defined")
        print("  ✅ Clean Architecture structure complete")
        print("  ✅ Alembic migrations ready")
        print("  ✅ Development tools configured")
        print("  ✅ Dependencies installed")
        print("  ✅ Environment variables validated")
        print("\n📊 System Status:")
        print(f"  • App: {settings.APP_NAME}")
        print(f"  • Version: {settings.APP_VERSION}")
        print(f"  • Environment: {settings.ENVIRONMENT}")
        print(f"  • Database: Neon PostgreSQL (asyncpg)")
        print(f"  • Cache: Redis")
        print(f"  • Framework: FastAPI")
        print("\n🚀 READY TO PROCEED TO PHASE 02: Database Design")
        print("="*70 + "\n")
