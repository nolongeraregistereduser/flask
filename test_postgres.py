# test_postgres.py
import psycopg2

try:
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host="localhost",
        database="flask_db",
        user="postgres",
        password="root"
    )
    
    # Open a cursor
    cur = conn.cursor()
    
    # Execute a simple query
    cur.execute("SELECT 1")
    result = cur.fetchone()
    print(f"Connection successful! Result: {result[0]}")
    
    # Close communication
    cur.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")