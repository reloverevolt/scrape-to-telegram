from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import urlparse
# from bitly_api import Connection
# from app.config import credentials
import gspread
import pandas as pd 
import telegram
import boto3
import redis
import os

# Instantiating postgress DB
DB_URL = os.environ.get("DATABASE_URL")
db_engine = create_engine(DB_URL) 	
Session = sessionmaker(bind=db_engine)
session = Session()
Base = automap_base()
Base.prepare(db_engine, reflect=True)
Products = Base.classes.banki

# Instantiating AWS S3
s3 = boto3.resource(
			service_name = "s3",
			region_name = os.environ.get("S3_REGION"),
			aws_access_key_id = os.environ.get("S3_KEY_ID"),
			aws_secret_access_key = os.environ.get("S3_SECRET_KEY")
			)
bucket = s3.Bucket(os.environ.get("S3_BUCKET"))

# Instantiating Redis DB

url = urlparse(os.environ.get("REDISCLOUD_URL"))
rds = redis.Redis(host=url.hostname, port=url.port, password=url.password)

# Instantiating Bitly API
# bitly = Connection(access_token = os.environ.get("BITLY_KEY"))

# Instantiating Telegram Bot

bot = telegram.Bot(token=os.environ.get("BOT_TOKEN"))

# Instantiating Google Sheets API

creds = os.environ.get("GS_ACCESS_FILE")

try:
	gc = gspread.service_account(filename=creds)

except FileNotFoundError:

	bucket.download_file(Key=creds, Filename=creds)
	gc = gspread.service_account(filename=creds)

sh = gc.open_by_key(os.environ.get("GS_KEY"))	
ws_refs = sh.worksheet("refferals")
ws_brands = sh.worksheet("brands")

service_table = pd.DataFrame(ws_refs.get_all_records())
brands_table = pd.DataFrame(ws_brands.get_all_records())
