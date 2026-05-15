# create_db.py
from src.services.database.db_connection import engine, create_tables
from sqlalchemy import text

print("Forcing database creation...")

# This will create the file
with engine.connect() as conn:
    conn.execute(text("SELECT 1"))
    print("Connection established → database.db should now exist")

create_tables()
print("Tables created")