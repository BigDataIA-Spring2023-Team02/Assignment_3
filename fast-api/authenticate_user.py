from http.client import HTTPException
from fastapi import APIRouter, Depends, status,HTTPException
from pytest import Session
import schemas, user_data, user_db_model
from jwt_api import bcrypt, verify, verify_token, create_access_token, get_current_user
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(
    tags=["Authentication"]
)

@router.post('/login')
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(user_data.get_db)):
    user = db.query(user_db_model.User_Table).filter(user_db_model.User_Table.username == request.username).first()
    if not user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="Invalid Credentials") 
    if not verify(user.password, request.password):
                raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="Incorrect Password")
    access_token = create_access_token(data={"sub": user.full_name})
    return {"access_token": access_token, "token_type": "bearer"}