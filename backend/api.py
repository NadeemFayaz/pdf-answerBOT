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
import uuid
from db import create_db, UploadPDFFile, RetrieveFile, RetrieveFiles, DeleteFile
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.llms import OpenAI
from getpass import getpass
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import HuggingFaceHub
from dotenv import load_dotenv


load_dotenv()

app = FastAPI()

if "HUGGINGFACEHUB_API_TOKEN" not in os.environ:
    print("SET HUGGINGFACEHUB_API_TOKEN")
    exit()

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

    
    fileId = UploadPDFFile(file_path)
    return {"message": "PDF uploaded successfully", "Id": fileId}    

# Endpoint for asking questions about the PDF
@app.post("/ask", response_class=JSONResponse)
async def ask_question(question: str = Form(...), file_id: str= Form(...)):
    try:

        filename = RetrieveFile(file_id)
        file_path = Path(UPLOAD_DIR) / filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found.")

        with fitz.open(file_path) as pdf:
            pdf_text = ""
            for page_num in range(pdf.page_count):
                page = pdf[page_num]
                pdf_text += page.get_text()
        
        # Search for the answer in the PDF text
        result = search_pdf_for_answer(question, pdf_text)
        logging.debug(f"Answer found: {result}")

        return {"answer": result}

    except Exception as e:
        logging.error(f"Error processing PDF or question: {str(e)}")
        return {"error": f"Error: {str(e)}"}

# Function to search PDF for the answer using section-based matching
def search_pdf_for_answer(question: str, text: str):
    # Step 1: Split PDF text into smaller, manageable sections
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_text(text)

    # Step 2: Create embeddings using Hugging Face and store them in a vector store (e.g., FAISS)
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    docsearch = FAISS.from_texts(texts, embeddings)

    # Step 3: Define the template and input variables for PromptTemplate
    prompt_template = PromptTemplate(
        input_variables=["question", "context"],
        template="Based on the following context, answer the question:\n\nContext:\n{context}\n\nQuestion:\n{question}"
    )

    # Generate a prompt by formatting the template with the question and context
    context = " ".join(texts)  # Join texts for simplicity, or use top relevant ones if applicable
    prompt = prompt_template.format(question=question, context=context)

    # Step 4: Use the Hugging Face language model to generate an answer based on the prompt
    llm = HuggingFaceHub(repo_id="google/flan-t5-base", model_kwargs={"temperature": 0})
    result = llm(prompt)

    return result


# Endpoint for retrieving the list of uploaded files
@app.get("/files", response_class=JSONResponse)
async def get_files():
    return RetrieveFiles()

#Endpoint for deleting a file
@app.delete("/files/{file_id}")
async def delete_file(file_id: str):
    filename = RetrieveFile(file_id)
    file_path = Path(UPLOAD_DIR) / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found.")

    os.remove(file_path)
    DeleteFile(file_id)
    return {"message": "File deleted successfully"}

