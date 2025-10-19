import databases
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE")
database = databases.Database(DATABASE_URL)
