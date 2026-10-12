"""
FastAPI Application Factory
Main entry point for Abundance Zone Youth Platform v2.0
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.database import create_tables, close_db_connections
from app.core.redis import close_redis_connections
from app.core.exceptions import DomainException

# Import routers
from app.api.v1 import (
    auth,
    users,
    branches,
    departments,
    youths,
    events,
    attendance,
    notifications,
)


# ─── Application Lifespan ────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager."""
    # ─── Startup ─────────────────────────────────────────────────────────────
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"📍 Environment: {settings.ENVIRONMENT}")
    print("🗄️  Database: Neon PostgreSQL (async)")
    print("⚡ Cache: Upstash Redis")

    # Create tables in development only
    if settings.ENVIRONMENT == "development":
        print("📊 Creating database tables...")
        await create_tables()

    print("✅ Application started successfully\n")

    yield  # Application is running

    # ─── Shutdown ────────────────────────────────────────────────────────────
    print("\n🛑 Shutting down application...")
    await close_db_connections()
    await close_redis_connections()
    print("✅ Cleanup complete")


# ─── Create FastAPI Application ──────────────────────────────────────────────
def create_app() -> FastAPI:
    """Application factory that creates and configures FastAPI instance."""
    app = FastAPI(
        title=settings.APP_NAME,
        description="Production-grade youth management system with Clean Architecture",
        version=settings.APP_VERSION,
        docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
        redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
        lifespan=lifespan,
    )

    # ─── Security Middleware ─────────────────────────────────────────────────
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=(
            settings.ALLOWED_HOSTS if settings.ENVIRONMENT == "production" else ["*"]
        ),
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
        expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining"],
    )

    # ─── Exception Handlers ──────────────────────────────────────────────────
    @app.exception_handler(DomainException)
    async def domain_exception_handler(request: Request, exc: DomainException):
        """Handle custom domain exceptions"""
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                },
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        """Handle Pydantic validation errors"""
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid request data",
                    "details": exc.errors(),
                },
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle HTTP exceptions"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": f"HTTP_{exc.status_code}",
                    "message": exc.detail,
                },
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions"""
        if settings.ENVIRONMENT == "development":
            import traceback

            print(f"❌ Unhandled exception: {exc}")
            traceback.print_exc()

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                },
            },
        )

    # ─── Health Check Endpoint ───────────────────────────────────────────────
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
        }

    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint"""
        return {
            "message": f"Welcome to {settings.APP_NAME}",
            "version": settings.APP_VERSION,
            "docs": "/docs" if settings.ENVIRONMENT != "production" else "disabled",
        }

    # ─── Include API Routers ─────────────────────────────────────────────────
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
    app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
    app.include_router(branches.router, prefix="/api/v1", tags=["Branches"])
    app.include_router(departments.router, prefix="/api/v1", tags=["Departments"])
    app.include_router(youths.router, prefix="/api/v1", tags=["Youths"])
    app.include_router(events.router, prefix="/api/v1", tags=["Events"])
    app.include_router(attendance.router, prefix="/api/v1", tags=["Attendance"])
    app.include_router(notifications.router, prefix="/api/v1", tags=["Notifications"])

    return app


# ─── Create Application Instance ─────────────────────────────────────────────
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        workers=settings.WORKERS,
    )
