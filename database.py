import databases
import os
from dotenv import load_dotenv

load_dotenv()


DATABASE_URL = os.getenv("DATABASE")
database = databases.Database(DATABASE_URL, statement_cache_size=0)
