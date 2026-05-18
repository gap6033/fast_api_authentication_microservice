from pydantic import BaseModel, EmailStr

class UserCreateRequest(BaseModel):
    email: EmailStr
    password: str

class UserCreateResponse(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserLoginResponse:
    access_token: str
    token_type: str = "bearer"

class UserDeleteResponse:
    id: int
    email: EmailStr