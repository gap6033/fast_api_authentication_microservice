from fastapi import APIRouter
from app.db.redis import get_redis
from app.core.config import settings

router = APIRouter()

@router.get("/")
def health_check():
    return {
        "status": "ok",
        "version": settings.VERSION,
        "service": settings.PROJECT_NAME
    }

@router.get("/redis")
def redis_health_check():
    try:
        redis = get_redis()
        # Test Redis connection by setting and getting a test value
        redis.set("test_key", "test_value")
        value = redis.get("test_key")
        redis.delete("test_key")  # Clean up
        
        if value == "test_value":
            return {
                "status": "ok",
                "message": "Redis connection successful",
                "version": settings.VERSION,
                "service": settings.PROJECT_NAME
            }
        else:
            return {
                "status": "error",
                "message": "Redis connection test failed",
                "version": settings.VERSION,
                "service": settings.PROJECT_NAME
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Redis connection failed: {str(e)}",
            "version": settings.VERSION,
            "service": settings.PROJECT_NAME
        } 