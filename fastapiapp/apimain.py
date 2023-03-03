import logging
import datetime
import user_db_model
from user_data import engine
from fastapi import FastAPI
from dotenv import load_dotenv
import noaa_database, aws_s3_files, aws_s3_fetchfile
import current_user, authenticate_user
from fastapi import FastAPI, APIRouter, Request

load_dotenv()

app = FastAPI()
user_db_model.Base.metadata.create_all(bind=engine)

# FastAPILimiter.add_limit(rate=1, per=1, key_func=lambda _: "global", scope=RateLimitItem.GLOBAL)

# FastAPILimiter.init(
#     app, 
#     key_func=lambda _: _.client.host,  # use client IP as the rate limit key
#     headers_enabled=True,  # enable headers for rate limit information
#     config=RateLimitsConfig,
# )

"""
Adding all the routers to call in the main FastAPI function app
"""
app.include_router(noaa_database.router)
app.include_router(aws_s3_files.router)
app.include_router(aws_s3_fetchfile.router)
app.include_router(current_user.router)
app.include_router(authenticate_user.router)
#app.include_router(ratelimit.router)
