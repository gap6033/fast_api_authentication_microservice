from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreateRequest
from app.core.security import hash_password


class UserRepository:
    def __init__(self, user_db: Session):
        self.user_db = user_db

    def get_user_by_email(self, email: str):
        return self.user_db.query(User).filter(User.email == email).first()

    def add(self, db_user: User) -> User:
        self.user_db.add(db_user)
        self.user_db.commit()
        self.user_db.refresh(db_user)
        return db_user

    def delete_by_email(self, email: str) -> bool:
        """Delete a user by email. Returns True if user was deleted, False if user not found."""
        user = self.get_user_by_email(email)
        if user:
            self.user_db.delete(user)
            self.user_db.commit()
            return True
        return False
