import databases

DATABASE_URL = "postgresql+asyncpg://myapp_user:superuser@localhost/myapp"

database = databases.Database(DATABASE_URL)