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
    
    # Execute query to get books with category names
    cur.execute("""
        SELECT b.id, b.title, b.author, c.name as category, b.status
        FROM books b
        JOIN categories c ON b.category_id = c.id
        ORDER BY b.id
    """)
    
    books = cur.fetchall()
    
    # Display books in a formatted way
    print("\n===== BOOKS IN DATABASE =====")
    print(f"{'ID':<4} {'TITLE':<30} {'AUTHOR':<20} {'CATEGORY':<15} {'STATUS':<10}")
    print("-" * 80)
    
    for book in books:
        book_id, title, author, category, status = book
        print(f"{book_id:<4} {title[:30]:<30} {author[:20]:<20} {category[:15]:<15} {status:<10}")
    
    # Get book count
    cur.execute("SELECT COUNT(*) FROM books")
    count = cur.fetchone()[0]
    print(f"\nTotal books in database: {count}")
    
    # Close communication
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")