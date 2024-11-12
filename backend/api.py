from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from datetime import datetime
from difflib import get_close_matches
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fastapi import HTTPException
import os
import sqlite3
import logging
import fitz  # PyMuPDF
from pathlib import Path

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "./uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize SQLite Database
def create_db():
    conn = sqlite3.connect('pdf_qa.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS documents (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        filename TEXT,
                        upload_date TEXT)''')
    conn.commit()
    conn.close()

create_db()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Endpoint for uploading PDF files
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    # Validate file type
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are allowed.")

    # Restrict file size to 10MB (10 * 1024 * 1024 bytes)
    MAX_FILE_SIZE = 10 * 1024 * 1024
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 10MB.")
    
    file_path = Path(UPLOAD_DIR) / file.filename
    
    # Prevent overwriting existing files
    if file_path.exists():
        new_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
        file_path = Path(UPLOAD_DIR) / new_filename

    # Save the file asynchronously
    with open(file_path, "wb") as buffer:
        buffer.write(content)

    # Save metadata in SQLite
    conn = sqlite3.connect('pdf_qa.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO documents (filename, upload_date) VALUES (?, ?)",
                   (file_path.name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

    return {"message": "PDF uploaded successfully", "filename": file_path.name}

# Endpoint for asking questions about the PDF
@app.post("/ask", response_class=JSONResponse)
async def ask_question(file: UploadFile = File(...), question: str = Form(...)):
    file_path = Path(UPLOAD_DIR) / file.filename

    try:
        logging.debug(f"Received question: {question}")

        # Check if the file already exists
        if not file_path.exists():
            async with file as f:
                with open(file_path, "wb") as buffer:
                    buffer.write(await f.read())

        # Extract text from the PDF
        doc = fitz.open(str(file_path))
        pdf_text = ""
        for page in doc:
            pdf_text += page.get_text("text")
            #logging.debug(f"Extracted PDF full text: {pdf_text}")

        #logging.debug(f"Extracted PDF text (first 500 chars): {pdf_text[:500]}")

        # Search for the answer in the PDF text
        result = search_pdf_for_answer(question, pdf_text)
        logging.debug(f"Answer found: {result}")

        return {"answer": result}

    except Exception as e:
        logging.error(f"Error processing PDF or question: {str(e)}")
        return {"error": f"Error: {str(e)}"}

# Endpoint to download a PDF file
@app.get("/download/{filename}")
async def download_pdf(filename: str):
    file_path = Path(UPLOAD_DIR) / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found.")
    
    return FileResponse(path=str(file_path), media_type='application/pdf', filename=filename)

# Endpoint to list all uploaded files
@app.get("/files")
async def list_files():
    files = os.listdir(UPLOAD_DIR)
    return {"files": files}

# Function to search PDF for the answer using section-based matching
def search_pdf_for_answer(question: str, text: str):
    paragraphs = text.split("\n\n")  # Split text into paragraphs (this assumes paragraphs are separated by empty lines)

    # Prepare the question and the paragraphs for comparison
    corpus = paragraphs + [question]  # Add the question to the corpus for comparison
    vectorizer = TfidfVectorizer(stop_words='english')  # Initialize TF-IDF vectorizer
    
    # Vectorize the text and the question
    tfidf_matrix = vectorizer.fit_transform(corpus)
    
    # Calculate cosine similarity between the question and each paragraph
    cosine_similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
    
    # Get the index of the most relevant paragraph
    most_relevant_idx = cosine_similarities.argmax()
    most_relevant_paragraph = paragraphs[most_relevant_idx]

    # Return a limited portion of the matching paragraph (top 3 sentences)
    sentences = most_relevant_paragraph.split('.')
    top_sentences = ' '.join(sentences[:3])  # Return first 3 sentences as context
    return top_sentences.strip() if top_sentences else "No relevant answer found."

# Function to split the text into sections
def split_into_sections(text):
    sections = {}
    current_section = None
    current_content = []
    headings = ["abstract", "introduction", "conclusion", "methodology", "literature review"]
    for line in text.splitlines():
        line = line.strip()
        if any(line.lower().startswith(heading) for heading in headings):
            if current_section:
                sections[current_section] = "\n".join(current_content)
            current_section = line
            current_content = []
        else:
            current_content.append(line)
    if current_section:
        sections[current_section] = "\n".join(current_content)
    return sections
