"""agent5/main.py"""
import os
import uuid

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent5.session_manager import get_or_create_session, reset_session
from agent5.orchestrator import handle_message

app = FastAPI(title="Agent 5 - Conversational Financial Assistant")

# Allow the Frontend folder's dev server to call this API.
# Tighten allow_origins to your actual frontend URL before deploying.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UPLOAD_DIR = os.path.join(PROJECT_ROOT, "agent5", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


class ChatRequest(BaseModel):
    session_id: str
    message: str


@app.post("/chat")
def chat(request: ChatRequest):
    """
    Main conversation endpoint. Send a session_id and message,
    get back Agent 5's reply.
    """
    memory = get_or_create_session(request.session_id)

    try:
        result = handle_message(memory, request.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "session_id": request.session_id,
        "type": result["type"],
        "text": result.get("text", result.get("data")),
    }


@app.post("/upload")
async def upload_file(
    session_id: str = Form(...),
    file: UploadFile = File(...),
):
    """
    Upload a bank statement PDF, passbook image, or CSV/Excel file.
    Saves it, registers it in the session's memory, and immediately
    advances the conversation (equivalent to the user saying
    "I've uploaded my file").
    """
    memory = get_or_create_session(session_id)

    # Save with a unique filename to avoid collisions across sessions.
    safe_name = f"{uuid.uuid4().hex}_{file.filename}"
    save_path = os.path.join(UPLOAD_DIR, safe_name)

    with open(save_path, "wb") as out_file:
        content = await file.read()
        out_file.write(content)

    memory.set_input("file_path", save_path)

    try:
        result = handle_message(memory, "I've uploaded my financial document.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "session_id": session_id,
        "type": result["type"],
        "text": result.get("text", result.get("data")),
    }


@app.post("/reset")
def reset(session_id: str):
    """Clear a session's memory to start a fresh conversation."""
    reset_session(session_id)
    return {"session_id": session_id, "status": "reset"}


@app.get("/health")
def health():
    return {"status": "ok"}