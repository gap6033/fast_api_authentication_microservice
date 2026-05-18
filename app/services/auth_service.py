from app.schemas.user import UserCreateRequest, UserLoginRequest, UserCreateResponse
from app.schemas.token import TokenLoginResponse, RefreshTokenRequest, AccessTokenRequest
from app.repositories.user_repository import UserRepository
from app.core.security import verify_password, hash_password, create_access_token, create_refresh_token, decode_access_token
from app.exceptions.user_exceptions import UserExistsException
from app.exceptions.auth_exceptions import InvalidCredentialsException
from app.models.user import User
from datetime import datetime, timezone, timedelta
from app.core.config import settings
from app.repositories.redis_repository import RedisRepository
import jwt
from app.core.logger import get_logger

logger = get_logger(__name__)

class AuthService:
    def __init__(self, user_db, redis):
        self.user_repo = UserRepository(user_db)
        self.redis_repo = RedisRepository(redis)

    def register(self, user: UserCreateRequest) -> UserCreateResponse:
        if self.user_repo.get_user_by_email(user.email):
            logger.warning(f"Failing Registration. Email {user.email} already registered")
            raise UserExistsException(f"{user.email} Email already registered")
        db_user = User(
            email=user.email,
            hashed_password=hash_password(user.password)
        )
        self.user_repo.add(db_user)
        logger.info(f"Registered new user with email: {user.email}")
        return UserCreateResponse(db_user.id, db_user.email)
    
    def login(self, user: UserLoginRequest) -> TokenLoginResponse:
        db_user = self.user_repo.get_user_by_email(user.email)
        if not db_user:
            logger.warning(f"User with email {user.email} not found")
        elif  not verify_password(user.password, db_user.hashed_password):
            logger.warning(f"Incorrect credentials provided for user {user.email}")
            raise InvalidCredentialsException
        access_token = self._generate_access_token(db_user.email)
        refresh_token = self._generate_refresh_token()
        refresh_token_expiry = int((timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)).total_seconds())
        self._add_refresh_token_to_redis(db_user, refresh_token, refresh_token_expiry)
        logger.info(f"User {db_user.email} logged in successfully")
        return TokenLoginResponse(access_token=access_token, token_type="bearer", refresh_token=refresh_token, refresh_token_expiry=refresh_token_expiry)
    
    def logout(self, access_token: AccessTokenRequest, refresh_token: RefreshTokenRequest):
        decoded_access_token = self._verify_access_token(access_token)
        exp_timestamp = decoded_access_token["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp, timezone.utc)
        ttl = max(0, int((exp_datetime - datetime.now(timezone.utc)).total_seconds())) 
        self.redis_repo.add(f"access_token:{access_token}", ttl, "1")
        self.redis_repo.remove(f"refresh_token: {refresh_token}")
        logger.info(f"User logout initiated. Access token blacklisted. Refresh token removed.")
        logger.info(f"User logout successful: {decoded_access_token["sub"]}")

    def delete_user(self, access_token: AccessTokenRequest, refresh_token: RefreshTokenRequest):
        logger.info(f"Deleting user: {user_email}")
        decoded_access_token = self._verify_access_token(access_token)
        ttl = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES).total_seconds()
        self.redis_repo.add(f"access_token:{access_token}", ttl, "1")
        self.redis_repo.remove(f"refresh_token: {refresh_token}")
        user_email = decoded_access_token["sub"]
        self.user_repo.delete_by_email(user_email)
        self.redis_repo.add(f"user_deleted:{user_email}", ttl, "1")
    
    def refresh_token(self, access_token, refresh_token):
        self._verify_refresh_token(refresh_token)
        payload = jwt.decode(
            access_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": False}  # 👈 disables expiration check
        )
        user_email = payload["sub"]
        access_token = self._generate_access_token(user_email)
        return access_token


    def _generate_access_token(self, user_email: int):
        to_encode={"sub": str(user_email)}
        expiry_time = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        expire = datetime.now(timezone.utc) + expiry_time
        to_encode.update({"exp": expire})
        return create_access_token(to_encode)

    def _generate_refresh_token(self):
        return create_refresh_token()
        
    def _add_refresh_token_to_redis(self, user: User, refresh_token: str, expiry_time: int):
        self.redis_repo.add(f"refresh_token:{refresh_token}", expiry_time, value=user.id)

    def _verify_access_token(self, token):
        decoded_access_token = decode_access_token(token)
        if self.redis_repo.get(f"access_token:{token}"):
            raise jwt.InvalidTokenError
        user_email = decoded_access_token["sub"]
        if self.redis_repo.get(f"user_deleted:{user_email}"):
            raise jwt.InvalidTokenError
        return decoded_access_token
    
    def _verify_refresh_token(self, refresh_token):
        if not self.redis_repo.get(f"refresh_token:{refresh_token}"):
            raise InvalidCredentialsException
        
