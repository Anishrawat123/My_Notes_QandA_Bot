from pathlib import Path
import shutil

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from pdf_reader import extract_text_from_pdf
from chunker import create_chunks
from embeddings import create_embeddings
from vector_db import create_vector_database
from retriever import retrieve_chunks
from generator import generate_answer


# ============================================================
# Configuration
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DOCUMENTS_DIR = BASE_DIR.parent / "documents"

# Make sure the documents directory exists
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="My Notes Q&A Bot",
    version="1.0.0",
    description="A RAG-based PDF Question Answering API",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Global RAG State
# ============================================================

chunks = []
index = None
current_file = None


# ============================================================
# Request Models
# ============================================================

class QuestionRequest(BaseModel):
    question: str


# ============================================================
# Startup
# ============================================================

@app.get("/")
def home():
    return {
        "message": "My Notes Q&A Bot is running",
        "status": "online",
    }


# ============================================================
# Upload PDF
# ============================================================

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    global chunks, index, current_file

    # Validate file type
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file was provided.",
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    # Prevent unsafe path handling by using only the filename
    safe_filename = Path(file.filename).name
    file_path = DOCUMENTS_DIR / safe_filename

    try:
        # ----------------------------------------------------
        # Save uploaded PDF
        # ----------------------------------------------------
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print(f"PDF saved to: {file_path}")

        # ----------------------------------------------------
        # PDF → Text
        # ----------------------------------------------------
        print("Extracting text...")
        text = extract_text_from_pdf(str(file_path))

        if not text or not text.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from the PDF.",
            )

        # ----------------------------------------------------
        # Text → Chunks
        # ----------------------------------------------------
        print("Creating chunks...")
        new_chunks = create_chunks(text)

        if not new_chunks:
            raise HTTPException(
                status_code=400,
                detail="No chunks could be created from the PDF.",
            )

        # ----------------------------------------------------
        # Chunks → Embeddings
        # ----------------------------------------------------
        print("Creating embeddings...")
        embeddings = create_embeddings(new_chunks)

        # ----------------------------------------------------
        # Embeddings → FAISS Vector Database
        # ----------------------------------------------------
        print("Creating vector database...")
        new_index = create_vector_database(embeddings)

        # ----------------------------------------------------
        # Update global state only after successful processing
        # ----------------------------------------------------
        chunks = new_chunks
        index = new_index
        current_file = safe_filename

        print("RAG system ready!")

        return {
            "message": "PDF uploaded successfully",
            "filename": current_file,
            "chunks": len(chunks),
        }

    except HTTPException:
        raise

    except Exception as e:
        print(f"Upload error: {e}")

        raise HTTPException(
            status_code=500,
            detail=f"Failed to process PDF: {str(e)}",
        )

    finally:
        await file.close()


# ============================================================
# Ask Question
# ============================================================

@app.post("/ask")
def ask_question(request: QuestionRequest):
    global chunks, index, current_file

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty.",
        )

    # Check whether a PDF has been uploaded
    if index is None or not chunks:
        return {
            "answer": "Please upload a PDF first.",
            "sources": [],
            "filename": None,
        }

    try:
        # ----------------------------------------------------
        # Question → Relevant Chunks
        # ----------------------------------------------------
        results = retrieve_chunks(
            question,
            chunks,
            index,
            top_k=3,
        )

        if not results:
            return {
                "question": question,
                "answer": "I could not find relevant information in the uploaded PDF.",
                "sources": [],
                "filename": current_file,
            }

        # ----------------------------------------------------
        # Chunks → LLM Answer
        # ----------------------------------------------------
        answer = generate_answer(
            question,
            results,
        )

        return {
            "question": question,
            "answer": answer,
            "sources": results,
            "filename": current_file,
        }

    except Exception as e:
        print(f"Question error: {e}")

        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate answer: {str(e)}",
        )