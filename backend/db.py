import sqlite3

def create_db():
    conn = sqlite3.connect('pdf_qa.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS documents (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        filename TEXT,
                        upload_date TEXT)''')
    conn.commit()
    conn.close()

create_db()  # Ensure the database is set up when the app starts
