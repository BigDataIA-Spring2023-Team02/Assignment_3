import pandas as pd
from typing import List
from sqlite3 import Connection
from sqlalchemy.orm import Session
import schemas, user_data, user_db_model
from fastapi import APIRouter, Depends, HTTPException, status
from database_file import get_database_file, get_user_data_file
from jwt_api import bcrypt, verify, verify_token, create_access_token, get_current_user

router = APIRouter(
    tags = ['Users']
)
get_db = user_data.get_db

@router.post('/user/create', response_model= schemas.ShowUser)
def create_user(request: schemas.User, db: Session = Depends(get_db)):
    user = db.query(user_db_model.User_Table).filter(user_db_model.User_Table.username == request.username).first()
    if not user:
        new_user = user_db_model.User_Table(full_name = request.full_name, username = request.username, password = bcrypt(request.password))
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User already exists')

@router.patch('/user/update',response_model= schemas.ShowUser)
def update_password(username : str, new_password: schemas.UpdatePassword, db: Session = Depends(get_db)):
    user = db.query(user_db_model.User_Table).filter(username == user_db_model.User_Table.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    updated_user = dict(username = username, password = bcrypt(new_password.password))
    for key, value in updated_user.items():
        setattr(user, key, value)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.get('/user/user_details', status_code=status.HTTP_200_OK)
async def user_details(username : str, current_user: schemas.User = Depends(get_current_user), userdb : Connection = Depends(get_user_data_file)):
    query = "SELECT user_type FROM all_users WHERE username==\'" + username +"\'"
    user_data = pd.read_sql_query(query, userdb)
    print(user_data)
    if user_data['user_type'].to_list() == ['Admin']:
        return user_data['user_type'].to_list()
    else:
        query2 = "SELECT plan FROM all_users WHERE username==\'" + username +"\'"
        user_data_2 = pd.read_sql_query(query2, userdb)
        plan = user_data_2['plan'].tolist()
        return plan

@router.post('/user/upgradeplan', status_code=status.HTTP_200_OK)
async def upgrade_plan(username : str, current_user: schemas.User = Depends(get_current_user), userdb : Connection = Depends(get_user_data_file)):
    query = "SELECT plan FROM all_users WHERE username=\'" + username +"\'"
    user_data = pd.read_sql_query(query, userdb)
    if user_data['plan'].iloc[0] == 'Free':
        user_data['plan'].iloc[0] = 'Gold'
    
    elif user_data['plan'].iloc[0] == 'Gold':
        user_data['plan'].iloc[0] = 'Platinum'
    
    cursor = userdb.cursor()
    update_query = "UPDATE all_users SET plan = ? WHERE username = ?"
    new_plan = user_data['plan'].iloc[0]
    username = username
    cursor.execute(update_query, (new_plan, username))
    userdb.commit()
    cursor.close()
    return True