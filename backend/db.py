from datetime import datetime
import sqlite3
import uuid

def create_db():
    conn = sqlite3.connect('pdf_qa1.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS documents (
                        fileId TEXT PRIMARY KEY,
                        filename TEXT,
                        upload_date TEXT)''')
    conn.commit()
    conn.close()

def UploadPDFFile(file_path):
    # create a random fileId
    fileId = str(uuid.uuid4())


    # Save metadata in SQLite
    conn = sqlite3.connect('pdf_qa1.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO documents (fileId, filename, upload_date) VALUES (?, ?, ?)", (fileId, file_path.name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

    return fileId


def RetrieveFile(fileId):
    conn = sqlite3.connect('pdf_qa1.db')
    cursor = conn.cursor()
    cursor.execute("SELECT filename FROM documents WHERE fileId = ?", (fileId,))
    result = cursor.fetchone()
    conn.close()
    if not result:
        return None
    return result[0]

def RetrieveFiles():
    conn = sqlite3.connect('pdf_qa1.db')
    cursor = conn.cursor()
    cursor.execute("SELECT fileId, filename, upload_date FROM documents")
    result = cursor.fetchall()
    conn.close()
    # return resultas JSON
    return [{"id": row[0], "name": row[1], "upload_date": row[2]} for row in result]

def DeleteFile(fileId):
    conn = sqlite3.connect('pdf_qa1.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM documents WHERE fileId = ?", (fileId,))
    conn.commit()
    conn.close()
    return


create_db()  # Ensure the database is set up when the app starts
