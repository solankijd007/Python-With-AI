"""
FastAPI main application.
Entry point for the API with middleware, routers, and startup events.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api.api_v1.api import api_router
from app.core.config import settings
from app.db.session import engine
from app.db.base import Base
from app import crud
from app.db.session import SessionLocal
from app.schemas.user import UserCreate


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Creates database tables and initial superuser on startup.
    """
    # Startup: Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create initial superuser if it doesn't exist (skip in test mode)
    if "sqlite" not in settings.DATABASE_URL.lower():
        db = SessionLocal()
        try:
            user = crud.crud_user.get_user_by_email(db, email=settings.FIRST_SUPERUSER_EMAIL)
            if not user:
                crud.crud_user.create_superuser(
                    db,
                    email=settings.FIRST_SUPERUSER_EMAIL,
                    password=settings.FIRST_SUPERUSER_PASSWORD,
                    full_name="Admin User"
                )
                print(f"✅ Created superuser: {settings.FIRST_SUPERUSER_EMAIL}")
            else:
                print(f"ℹ️  Superuser already exists: {settings.FIRST_SUPERUSER_EMAIL}")
        except Exception as e:
            print(f"⚠️  Error creating superuser: {e}")
        finally:
            db.close()
    
    yield
    
    # Shutdown: cleanup if needed
    pass


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
    ## FastAPI PostgreSQL CRUD Application
    
    A production-ready REST API with:
    
    * **JWT Authentication** - Access and refresh tokens
    * **User Management** - Registration, login, profile management
    * **Item Management** - CRUD operations with ownership verification
    * **PostgreSQL Database** - SQLAlchemy ORM with Alembic migrations
    * **Security** - Password hashing, token validation, permission checks
    * **API Versioning** - Structured v1 API with room for future versions
    
    ### Authentication
    
    1. Register a new user at `/api/v1/auth/register`
    2. Login at `/api/v1/auth/login` to receive access and refresh tokens
    3. Use the access token in the `Authorization: Bearer <token>` header
    4. Refresh your access token at `/api/v1/auth/refresh` when it expires
    
    ### Default Superuser
    
    - **Email**: admin@example.com
    - **Password**: admin123
    
    ⚠️ **Change these credentials in production!**
    """,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Global exception handler for database errors
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle SQLAlchemy database errors."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Database error occurred. Please try again later."},
    )


# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint.
    Returns API status and version.
    """
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "project": settings.PROJECT_NAME,
    }


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "Welcome to FastAPI PostgreSQL CRUD API",
        "version": settings.VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }
