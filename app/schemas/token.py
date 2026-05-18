from pydantic import BaseModel

class TokenLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    refresh_token_expiry: int
    

class RefreshTokenRequest(BaseModel):
    token: str

class AccessTokenRequest(BaseModel):
    token: str