from typing import Optional
from enum import Enum
from pydantic import BaseModel

class User(BaseModel):
    full_name: str
    username : str
    password: str
    plan : str

class ShowUser(BaseModel):
    username: str
    class Config():
        orm_mode = True

class Login(BaseModel):
    username: str
    password: str
    plan: str

class UserPlan(str, Enum):
    FREE = "free"
    GOLD = "gold"
    PLATINUM = "platinum"

class RateLimitsConfig:
    RATE_LIMITS = {
        UserPlan.FREE: 10,
        UserPlan.GOLD: 15,
        UserPlan.PLATINUM: 20,
    }
    RATE_LIMIT_RESET_TIME = 60 * 60  # 60 minutes in seconds

class PasswordReset(BaseModel):
    username: str
    new_password: str
    confirm_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None