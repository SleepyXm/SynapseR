import databases
import os

DATABASE_URL = os.environ.get("DATABASE")
database = databases.Database(DATABASE_URL, min_size=1, max_size=2)
