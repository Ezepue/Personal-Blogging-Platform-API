from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os
from pathlib import Path

router = APIRouter()

# Define upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """Handles media file uploads"""
    file_location = UPLOAD_DIR / file.filename

    try:
        with file_location.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

    return {"filename": file.filename, "url": f"/uploads/{file.filename}"}
