import user_db_model
from user_data import engine
from fastapi import FastAPI
from dotenv import load_dotenv
import noaa_database, aws_s3_files, aws_s3_fetchfile
import current_user, authenticate_user

load_dotenv()

app = FastAPI()
user_db_model.Base.metadata.create_all(bind = engine)

"""
Adding all the routers to call in the main FastAPI function app
"""
app.include_router(noaa_database.router)
app.include_router(aws_s3_files.router)
app.include_router(aws_s3_fetchfile.router)
app.include_router(current_user.router)
app.include_router(authenticate_user.router)