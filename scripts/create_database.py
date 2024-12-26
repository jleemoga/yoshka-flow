import os
import sys

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import psycopg2
from app.core.config import get_settings

def read_sql_file():
    """Read the SQL script from the docs folder"""
    script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                              'docs', 'doc.database_script.md')
    with open(script_path, 'r') as file:
        return file.read()

def execute_sql_script():
    """Execute the SQL script against the database"""
    settings = get_settings()
    
    print("Connecting to database...")
    conn = psycopg2.connect(settings.POSTGRES_URL)
    conn.autocommit = True
    
    try:
        with conn.cursor() as cur:
            print("Executing SQL script...")
            sql_script = read_sql_file()
            cur.execute(sql_script)
            print("Database schema created successfully!")
    except Exception as e:
        print(f"Error creating database schema: {str(e)}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    execute_sql_script()
