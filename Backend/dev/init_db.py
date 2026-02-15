"""
Initialize database by running the SQL schema
"""
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

# Read the SQL file
with open('Table_postgres.sql', 'r') as f:
    sql_commands = f.read()

# Connect to database
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

try:
    # Execute the SQL commands
    cur.execute(sql_commands)
    conn.commit()
    print("✅ Database tables created successfully!")
except Exception as e:
    conn.rollback()
    print(f"❌ Error creating tables: {e}")
finally:
    cur.close()
    conn.close()
