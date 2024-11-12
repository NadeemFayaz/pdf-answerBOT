import sqlite3

def create_db():
    conn = sqlite3.connect('pdf_qa1.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS documents (
                        fileId TEXT PRIMARY KEY,
                        filename TEXT,
                        upload_date TEXT)''')
    conn.commit()
    conn.close()

create_db()  # Ensure the database is set up when the app starts
