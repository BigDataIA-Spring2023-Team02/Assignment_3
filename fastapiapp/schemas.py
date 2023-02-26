from typing import Optional
from pydantic import BaseModel

class User(BaseModel):
    full_name: str
    username : str
    password: str

class ShowUser(BaseModel):
    username: str
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