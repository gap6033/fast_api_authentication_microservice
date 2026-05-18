import jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from app.core.config import settings
import secrets

# Password hashing (already defined)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    """Create access token"""
    return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str):
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

def create_refresh_token():
    return secrets.token_urlsafe(32)
    # Store user_id as value, set expiration
    redis_client.setex(f"opaque_token:{token}", timedelta(minutes=expires_in_minutes), value=user_id)
    return token

# def verify_opaque_token(token: str):
#     user_id = redis_client.get(f"opaque_token:{token}")
#     if user_id is None:
#         return None  # Invalid or expired token
#     return user_id  # Valid token

# def revoke_opaque_token(token: str):
#     redis_client.delete(f"opaque_token:{token}")



# # JWT token verification
# def verify_access_token(token: str) -> dict:
#     try:
#         # Check if token is blacklisted
#         if is_blacklisted(token):
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Invalid Token"
#             )
            
#         
#     except jwt.ExpiredSignatureError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Token has expired"
#         )
#     except jwt.InvalidTokenError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid token"
#         )
    
# def invalidate_access_token(token: str) -> None:
#     """Add token to blacklist"""
#     add_to_blacklist(token)

# def create_refresh_token(data: dict) -> str:
#     to_encode = data.copy()
#     expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
#     return encoded_jwt
    

# def verify_refresh_token(token: str):
#     if not is_whitelisted(token):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid Token"
#         )
#     try: 
#         return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
#     except jwt.ExpiredSignatureError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Token has expired"
#         )
#     except jwt.InvalidTokenError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid token"
#         )
    
# def invalidate_refresh_token(token: str) -> None:
#     """Add token to blacklist"""
#     remove_from_whitelist(token)
