import ebooklib.epub
from fastapi import FastAPI, Request, UploadFile, File, HTTPException, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import io
from pdfminer.high_level import extract_text
import ebooklib
from docx import Document
from PIL import Image
import pytesseract
from sentence_transformers import SentenceTransformer
import numpy as np
import re

# FastAPI app setup
app = FastAPI()

# Add CORS middleware
origins = [
    "*",
    "https://bookmuncha.onrender.com",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "X_API_KEY"]
)


# Load embedding model
embedding_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

def split_into_paragraphs(text):
    # Normalize spaces and remove excessive newlines
    text = re.sub(r'\n+', '\n', text)  # Replace multiple newlines with a single newline

    # Split by double newline (\n\n) to create a rough paragraph structure
    paragraphs = text.split('\n\n')

    paragraph_data = []

    for para_num, para_text in enumerate(paragraphs, start=1):
        # Strip extra spaces and check if the paragraph is non-empty
        para_text = para_text.strip()

        # Avoid combining paragraphs from different sections or books:
        # Look for common indicators like chapter headers, page breaks, or markers
        if len(para_text) < 50:  # Threshold for very short paragraphs
            # Try splitting even further if the paragraph is too short
            sub_paragraphs = para_text.split('\n\n')
            for sub_para_num, sub_para_text in enumerate(sub_paragraphs, start=1):
                sub_para_text = sub_para_text.strip()
                if sub_para_text:
                    paragraph_data.append({
                        "paragraph_number": para_num,
                        "text": sub_para_text,
                        "embedding": embedding_model.encode(sub_para_text).tolist()
                    })
        else:
            # Check for unusual content patterns (e.g., headings or page markers) that could indicate breaks
            if re.match(r'(Chapter|Section) \d+', para_text):
                # Treat this as a new section, perhaps adding a special flag
                paragraph_data.append({
                    "paragraph_number": para_num,
                    "text": para_text,
                    "embedding": embedding_model.encode(para_text).tolist(),
                    "is_section_heading": True  # Flagging as a section heading
                })
            else:
                # Regular paragraph handling
                if para_text:
                    paragraph_data.append({
                        "paragraph_number": para_num,
                        "text": para_text,
                        "embedding": embedding_model.encode(para_text).tolist()
                    })

    return paragraph_data

def process_file(file_stream, file_type):
    file_stream = io.BytesIO(file_stream)

    if file_type == 'pdf':
        file_stream.seek(0)
        text = extract_text(file_stream)
        pages = text.split('\f')  # Split by form feed to simulate pages
    elif file_type == 'epub':
        file_stream.seek(0)
        book = ebooklib.epub.read_epub(file_stream)
        text = ""
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                text += item.get_body_content().decode('utf-8')
        pages = text.split('\f')  # Simulate page breaks in EPUB
    elif file_type == 'docx':
        file_stream.seek(0)
        doc = Document(file_stream)
        text = "\n".join([para.text for para in doc.paragraphs])
        pages = text.split('\f')  # Simulate page breaks for docx (not very accurate)
    elif file_type in ('jpg', 'jpeg', 'png'):
        file_stream.seek(0)
        img = Image.open(file_stream)
        text = pytesseract.image_to_string(img)
        pages = text.split('\f')  # Simulate page breaks for images
    else:
        raise ValueError("Unsupported file type")

    # Handle page breaks more cleanly
    page_data = []
    for page_num, page_text in enumerate(pages, start=1):
        paragraphs = split_into_paragraphs(page_text)
        for para in paragraphs:
            para["page_number"] = page_num  # Assign the page number
            page_data.append(para)

    return page_data

# Upload endpoint
@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...), request: Request = None):


    file_type = file.filename.rsplit('.', 1)[-1].lower()

    try:
        file_content = await file.read()
        chunks = process_file(file_content, file_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return JSONResponse(content={"chunks": chunks}, status_code=200)

# Answer endpoint (modified to avoid summarization)
@app.post("/api/answer")
async def get_answers(request: Request, data: dict = Body(...)):

    question = data.get("question", "")
    chunks = data.get("chunks", [])
    result_limit = int(data.get("limit", 5))

    if not question:
        raise HTTPException(status_code=400, detail="Question is required")
    if not chunks:
        raise HTTPException(status_code=400, detail="Chunks are required")

    try:
        question_embedding = embedding_model.encode(question)
        similarities = []

        for chunk in chunks:
            chunk_embedding = np.array(chunk["embedding"])
            similarity = np.dot(question_embedding, chunk_embedding) / (
                np.linalg.norm(question_embedding) * np.linalg.norm(chunk_embedding)
            )
            similarities.append((chunk, similarity))

        similarities.sort(key=lambda x: x[1], reverse=True)
        relevant_chunks = [x[0] for x in similarities[:result_limit]]

        # No summarization here, just return the relevant chunks
        answers = [{"page_number": chunk["page_number"], "text": chunk["text"]} for chunk in relevant_chunks]

        return JSONResponse(content={"answers": answers}, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
