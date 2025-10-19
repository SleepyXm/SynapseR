import databases
import os

DATABASE_URL = os.environ.get("DATABASE")
database = databases.Database(DATABASE_URL, statement_cache_size=0)
