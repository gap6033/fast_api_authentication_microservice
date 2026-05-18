from fastapi import FastAPI
from app.api.v1 import auth, health, protected
from app.db.base import Base
from app.db.session import engine
# from app.api.v1.protected import router as protected_router
from fastapi import FastAPI
from app.middlewares.logging import LoggingMiddleware  # adjust import path

app = FastAPI()


# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(LoggingMiddleware)

# Include routes
app.include_router(auth.router, prefix="/v1/auth", tags=["auth"])
app.include_router(health.router, prefix="/v1/health", tags=["health"])

