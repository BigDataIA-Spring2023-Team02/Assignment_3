from user_data import Base
from sqlalchemy import Column, Integer, String

class User_Table(Base):
    __tablename__ = "all_users"
    
    id = Column(Integer, primary_key= True, index=True)
    full_name = Column(String)
    username = Column(String)
    password = Column(String)
    plan = Column(String)
    role = Column(String)