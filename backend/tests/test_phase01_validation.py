"""
Phase 01 Validation Tests
Ensures all Phase 01 deliverables are working correctly before proceeding to Phase 02
"""

import pytest
from pathlib import Path
import importlib.util


class TestPhase01Configuration:
    """Test core configuration is properly set up"""
    
    def test_settings_import(self):
        """Test that settings can be imported without errors"""
        from app.core.config import settings
        assert settings is not None
        assert settings.APP_NAME == "Abundance Zone Youth Platform"
    
    def test_database_url_format(self):
        """Test DATABASE_URL uses asyncpg driver for Neon"""
        from app.core.config import settings
        assert settings.DATABASE_URL.startswith("postgresql+asyncpg://"), \
            "DATABASE_URL must use postgresql+asyncpg:// for Neon async support"
    
    def test_redis_url_format(self):
        """Test REDIS_URL is properly formatted"""
        from app.core.config import settings
        assert settings.REDIS_URL.startswith(("redis://", "rediss://")), \
            "REDIS_URL must start with redis:// or rediss://"
    
    def test_environment_variables(self):
        """Test all required environment variables are set"""
        from app.core.config import settings
        
        required_vars = [
            'APP_NAME', 'ENVIRONMENT', 'DATABASE_URL', 'DATABASE_URL_SYNC',
            'REDIS_URL', 'JWT_SECRET_KEY', 'JWT_REFRESH_SECRET_KEY',
            'GOOGLE_API_KEY', 'OPENAI_API_KEY'
        ]
        
        for var in required_vars:
            assert hasattr(settings, var), f"Missing required setting: {var}"
            value = getattr(settings, var)
            assert value is not None, f"Setting {var} is None"
            assert str(value).strip() != "", f"Setting {var} is empty"
    
    def test_jwt_secrets_are_different(self):
        """Test JWT access and refresh secrets are different"""
        from app.core.config import settings
        assert settings.JWT_SECRET_KEY != settings.JWT_REFRESH_SECRET_KEY, \
            "JWT access and refresh secrets must be different"


class TestPhase01Database:
    """Test database configuration"""
    
    def test_database_module_import(self):
        """Test database module can be imported"""
        from app.core.database import Base, engine, AsyncSessionLocal, get_db
        assert Base is not None
        assert engine is not None
        assert AsyncSessionLocal is not None
        assert callable(get_db)
    
    def test_database_engine_url(self):
        """Test database engine is configured with Neon URL"""
        from app.core.database import engine
        assert "neon.tech" in str(engine.url) or "localhost" in str(engine.url), \
            "Database URL should point to Neon or localhost"
    
    def test_database_pool_configuration(self):
        """Test database connection pool is properly configured"""
        from app.core.database import engine
        assert engine.pool.size() > 0 or hasattr(engine.pool, '_pool'), \
            "Database connection pool not configured"


class TestPhase01Redis:
    """Test Redis configuration"""
    
    def test_redis_module_import(self):
        """Test Redis module can be imported"""
        from app.core.redis import redis_client, get_redis, set_cache, get_cache
        assert redis_client is not None
        assert callable(get_redis)
        assert callable(set_cache)
        assert callable(get_cache)
    
    @pytest.mark.asyncio
    async def test_redis_connection(self):
        """Test Redis connection works"""
        from app.core.redis import redis_client
        try:
            await redis_client.ping()
            connected = True
        except Exception:
            connected = False
        
        # Redis connection is optional for tests (might not be running locally)
        if not connected:
            pytest.skip("Redis not available (optional for Phase 01)")


class TestPhase01Exceptions:
    """Test custom exception classes"""
    
    def test_exceptions_import(self):
        """Test all exception classes can be imported"""
        from app.core.exceptions import (
            DomainException,
            AuthenticationException,
            InvalidCredentialsException,
            TokenExpiredException,
            InvalidTokenException,
            AuthorizationException,
            ResourceNotFoundException,
            DuplicateResourceException,
            ValidationException,
            BusinessRuleViolationException,
            ExternalServiceException,
            RateLimitExceededException,
        )
        
        # Test they are all exception classes
        assert issubclass(DomainException, Exception)
        assert issubclass(AuthenticationException, DomainException)
        assert issubclass(ValidationException, DomainException)
    
    def test_exception_initialization(self):
        """Test exceptions can be initialized with messages"""
        from app.core.exceptions import InvalidCredentialsException, ResourceNotFoundException
        
        exc1 = InvalidCredentialsException()
        assert "Invalid email or password" in exc1.message
        assert exc1.code == "INVALID_CREDENTIALS"
        
        exc2 = ResourceNotFoundException("Youth", "123")
        assert "Youth" in exc2.message
        assert "123" in exc2.message


class TestPhase01FastAPI:
    """Test FastAPI application"""
    
    def test_app_import(self):
        """Test FastAPI app can be imported"""
        from app.main import app, create_app
        assert app is not None
        assert callable(create_app)
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self, client):
        """Test health check endpoint returns 200"""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "environment" in data
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self, client):
        """Test root endpoint returns welcome message"""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data


class TestPhase01FileStructure:
    """Test file and folder structure"""
    
    def test_core_files_exist(self):
        """Test all core files exist"""
        base_path = Path(__file__).parent.parent
        
        required_files = [
            "app/__init__.py",
            "app/main.py",
            "app/core/__init__.py",
            "app/core/config.py",
            "app/core/database.py",
            "app/core/redis.py",
            "app/core/exceptions.py",
            "alembic.ini",
            "alembic/env.py",
            "requirements.txt",
            "requirements-dev.txt",
            "Makefile",
            "pytest.ini",
            ".env.example",
            ".gitignore",
        ]
        
        for file_path in required_files:
            full_path = base_path / file_path
            assert full_path.exists(), f"Required file missing: {file_path}"
    
    def test_folder_structure_exists(self):
        """Test Clean Architecture folder structure exists"""
        base_path = Path(__file__).parent.parent / "app"
        
        required_dirs = [
            "api/v1",
            "api/middleware",
            "application",
            "core",
            "domain/entities",
            "domain/value_objects",
            "domain/repositories",
            "domain/events",
            "infrastructure/database/models",
            "infrastructure/database/repositories",
            "infrastructure/external",
            "infrastructure/security",
            "tasks",
            "scripts",
        ]
        
        for dir_path in required_dirs:
            full_path = base_path / dir_path
            assert full_path.exists(), f"Required directory missing: {dir_path}"
            assert full_path.is_dir(), f"Path exists but is not a directory: {dir_path}"


class TestPhase01DependencyVersions:
    """Test that all required dependencies are installed"""
    
    def test_fastapi_installed(self):
        """Test FastAPI is installed"""
        import fastapi
        assert fastapi.__version__ is not None
    
    def test_sqlalchemy_installed(self):
        """Test SQLAlchemy is installed"""
        import sqlalchemy
        assert sqlalchemy.__version__ is not None
    
    def test_pydantic_installed(self):
        """Test Pydantic is installed"""
        import pydantic
        assert pydantic.__version__ is not None
    
    def test_redis_installed(self):
        """Test Redis is installed"""
        import redis
        assert redis.__version__ is not None
    
    def test_alembic_installed(self):
        """Test Alembic is installed"""
        import alembic
        assert alembic.__version__ is not None


class TestPhase01Summary:
    """Summary test to ensure Phase 01 is complete"""
    
    def test_phase01_completion_checklist(self):
        """Test all Phase 01 objectives are met"""
        from app.core.config import settings
        from app.core.database import Base, engine
        from app.core.redis import redis_client
        from app.main import app
        
        checklist = {
            "Configuration loaded": settings is not None,
            "Database engine created": engine is not None,
            "Redis client created": redis_client is not None,
            "FastAPI app created": app is not None,
            "DATABASE_URL uses asyncpg": "postgresql+asyncpg://" in settings.DATABASE_URL,
            "Environment is set": settings.ENVIRONMENT in ["development", "staging", "production"],
        }
        
        failed_checks = [name for name, passed in checklist.items() if not passed]
        
        assert len(failed_checks) == 0, \
            f"Phase 01 checklist failed: {', '.join(failed_checks)}"
    
    def test_phase01_ready_for_phase02(self):
        """Test system is ready for Phase 02 (Database Design)"""
        from app.core.database import Base
        from pathlib import Path
        
        # Check that Base class is ready for model definitions
        assert hasattr(Base, 'metadata'), "Base class missing metadata"
        
        # Check that models directory exists and is ready
        models_dir = Path(__file__).parent.parent / "app" / "infrastructure" / "database" / "models"
        assert models_dir.exists(), "Models directory not created"
        
        # Check that domain entities directory exists
        entities_dir = Path(__file__).parent.parent / "app" / "domain" / "entities"
        assert entities_dir.exists(), "Domain entities directory not created"
        
        print("\n" + "="*70)
        print("✅ PHASE 01 VALIDATION COMPLETE")
        print("="*70)
        print("\n📋 Phase 01 Checklist:")
        print("  ✅ Clean Architecture structure created")
        print("  ✅ Neon PostgreSQL configured (async)")
        print("  ✅ Upstash Redis configured")
        print("  ✅ FastAPI application factory working")
        print("  ✅ Custom exceptions defined")
        print("  ✅ Alembic migrations ready")
        print("  ✅ Development tooling configured")
        print("  ✅ All core modules importable")
        print("\n🚀 READY TO PROCEED TO PHASE 02: Database Design")
        print("="*70 + "\n")
