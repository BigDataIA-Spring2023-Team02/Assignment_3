from http.client import HTTPException
from fastapi import APIRouter, Depends, status,HTTPException
from pytest import Session
import schemas, user_data, user_db_model
from jwt_api import bcrypt, verify, verify_token, create_access_token, get_current_user
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
import jwt_api

# Create router object
router = APIRouter(
    tags=["authentication"]
)

# Create route for user login
@router.post('/login')
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(user_data.get_user_data)):
    """
    Login to the system and generate access token to get full access of the application
    """
    # Query database for user based on provided username
    user = db.query(user_db_model.User_Table).filter(user_db_model.User_Table.username == request.username).first()
    
    # If user does not exist, raise HTTP 404 error
    if not user:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="Invalid Credentials") 
    
    # If password is incorrect, raise HTTP 404 error
    if not verify(user.password, request.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incorrect Password")
    
    # Create JWT access token for authenticated user
    access_token = create_access_token(data={"sub": user.full_name})
    
    # Return access token and bearer token type
    return {"access_token": access_token, "token_type": "bearer"}

@router.post('/reset')
def reset_password(request: schemas.PasswordReset, db: Session = Depends(user_data.get_user_data)):
    """
    Reset the password for a given user.
    """
    # Check if the new password and confirm password fields match
    if request.new_password != request.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password and confirm password do not match.")
    
    # Query the database for the user with the provided username
    user = db.query(user_db_model.User_Table).filter(user_db_model.User_Table.username == request.username).first()
    
    # If the user does not exist, raise HTTP 404 error
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    
    # Hash the new password
    hashed_password = jwt_api.bcrypt(request.new_password)
    
    # Update the user's password in the database
    user.password = hashed_password
    db.commit()
    db.refresh(user)

    # Returning the newly created user object
    return user

    # # Create a new access token for the user with the updated password
    # access_token = jwt_api.create_access_token(data={"sub": user.full_name})
    
    # # Return the access token and bearer token type
    # return {"access_token": access_token, "token_type": "bearer"}