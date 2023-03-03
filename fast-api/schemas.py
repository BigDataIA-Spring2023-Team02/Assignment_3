from enum import Enum 
from typing import Optional
from pydantic import BaseModel

class User(BaseModel):
    full_name: str
    username : str
    password: str
    plan : str
    user_type : str

class ShowUser(BaseModel):
    username: str
    class Config():
        orm_mode = True

class UpdatePassword(BaseModel):
    password : str    
    class Config():
        orm_mode = True

class Login(BaseModel):
    username: str
    password : str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class Plan(str, Enum):
    free = 'Free'
    gold = 'Gold'
    platinum = 'Platinum'