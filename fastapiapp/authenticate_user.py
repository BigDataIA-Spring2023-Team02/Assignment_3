from http.client import HTTPException
from fastapi import APIRouter, Depends, status,HTTPException
from pytest import Session
import schemas, user_data, user_db_model
from jwt_api import bcrypt, verify, verify_token, create_access_token, get_current_user
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

# Create router object
router = APIRouter(
    tags=["authentication"]
)

# Create route for user login
@router.post('/login')
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(user_data.get_db)):
    # Query database for user based on provided username
    user = db.query(user_db_model.User_Table).filter(user_db_model.User_Table.username == request.username).first()
    
    # If user does not exist, raise HTTP 404 error
    if not user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="Invalid Credentials") 
    
    # If password is incorrect, raise HTTP 404 error
    if not verify(user.password, request.password):
                raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="Incorrect Password")
    
    # Create JWT access token for authenticated user
    access_token = create_access_token(data={"sub": user.full_name})
    
    # Return access token and bearer token type
    return {"access_token": access_token, "token_type": "bearer"}