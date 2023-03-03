from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
import schemas, user_data, user_db_model
from sqlalchemy.orm import Session
from jwt_api import bcrypt, verify, verify_token, create_access_token, get_current_user

# Creating a router object with tag 'users'
router = APIRouter(
    tags = ['users']
)

# Getting the database object using dependency injection
get_user_db = user_data.get_user_data

# Creating a POST route to create a new user
@router.post('/user/create', response_model= schemas.ShowUser)
def create_user(request: schemas.User, database: Session = Depends(get_user_db)):
    """
    Create a new user and add it into user database to login to the system
    """
    # Creating a new user object with hashed password
    user = user_db_model.User_Table(full_name = request.full_name, username = request.username, password = bcrypt(request.password), plan = request.plan)
    
    # Adding the new user to the database
    database.add(user)
    database.commit()

    # Refreshing the new user object to update its fields
    database.refresh(user)

    # Returning the newly created user object
    return user

    