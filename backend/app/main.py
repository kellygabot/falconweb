from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.db.mongo import connect_mongo, disconnect_mongo
from app.db.postgres import Base, engine
from app.api import auth, grades, attendance, users, files, facebook, school

logger = logging.getLogger(__name__)

# Create all database tables (skip if database unavailable)
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    logger.warning(f"Could not create database tables on startup: {e}")
    logger.info("Make sure PostgreSQL is configured and running")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_mongo()
    yield
    # Shutdown
    await disconnect_mongo()


app = FastAPI(
    title="Falcon School API",
    description="Centralized grading and school management system",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],  # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(school.router, prefix="/api/school", tags=["school"])
app.include_router(grades.router, prefix="/api/grades", tags=["grades"])
app.include_router(attendance.router, prefix="/api/attendance", tags=["attendance"])
app.include_router(files.router, prefix="/api/files", tags=["files"])
app.include_router(facebook.router, prefix="/api/facebook", tags=["facebook"])


@app.get("/health")
async def health_check():
    return {"status": "ok"}
