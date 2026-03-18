import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def create_db():
    try:
        # Connect to the default 'postgres' database
        con = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            host='localhost',
            password='Gd012354R1.'
        )
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = con.cursor()
        
        # Check if database exists
        cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'futadmin'")
        exists = cur.fetchone()
        
        if not exists:
            cur.execute('CREATE DATABASE futadmin')
            print("Database 'futadmin' created successfully.")
        else:
            print("Database 'futadmin' already exists.")
            
        cur.close()
        con.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_db()
