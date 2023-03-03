import user_db_model
from fastapi import FastAPI
from user_data import engine
from dotenv import load_dotenv
import current_user, authenticate_user
from router import noaa_database, aws_s3_files, aws_s3_fetchfile, user_logs

load_dotenv()

app = FastAPI()
user_db_model.Base.metadata.create_all(bind = engine)

app.include_router(noaa_database.router)
app.include_router(aws_s3_files.router)
app.include_router(aws_s3_fetchfile.router)
app.include_router(current_user.router)
app.include_router(authenticate_user.router)
app.include_router(user_logs.router)