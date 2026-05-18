from fastapi import Depends
from app.db.session import get_db
from app.db.redis import get_redis
from app.services.auth_service import AuthService
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/login")

def get_auth_service(user_db = Depends(get_db), redis = Depends(get_redis)):
    return AuthService(user_db, redis)
