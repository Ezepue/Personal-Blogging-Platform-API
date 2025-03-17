from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from utils.auth_helpers import get_current_user
from models.user import UserDB

import shutil
import os
import logging
from pathlib import Path
import uuid

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Define the upload directory
UPLOAD_DIR = Path("uploads")
MAX_FILE_SIZE_MB = 10  # Maximum allowed file size in MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".pdf", ".mp4"}

def ensure_upload_dir():
    """Ensure the upload directory exists before use."""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def get_unique_filename(filename: str) -> str:
    """Generate a unique filename to prevent overwriting."""
    if not filename:
        raise HTTPException(status_code=400, detail="Filename cannot be empty")

    extension = Path(filename).suffix.lower()

    # Ensure the file type is allowed
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    return f"{uuid.uuid4().hex}{extension}"

def validate_file_size(file: UploadFile):
    """Ensure the uploaded file is within the allowed size limit."""
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)

    max_size_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
    if file_size > max_size_bytes:
        raise HTTPException(status_code=413, detail=f"File size exceeds {MAX_FILE_SIZE_MB}MB limit")

def validate_and_sanitize_filename(filename: str) -> Path:
    """Sanitize and return a safe file path."""
    # Prevent directory traversal attack (../)
    safe_filename = Path(filename).name
    return UPLOAD_DIR / safe_filename

@router.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    current_user: UserDB = Depends(get_current_user)  # Requires authentication
):
    """Handles secure media file uploads (Authenticated Users Only)."""
    ensure_upload_dir()
    validate_file_size(file)

    filename = get_unique_filename(file.filename)
    file_location = UPLOAD_DIR / filename

    try:
        with file_location.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"User {current_user.id} uploaded file: {file_location}")
    except Exception as e:
        logger.error(f"File upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

    return {"filename": filename, "url": f"/media/{filename}"}


@router.get("/files/")
def list_files():
    """Returns a list of uploaded files."""
    ensure_upload_dir()

    try:
        files = [file.name for file in UPLOAD_DIR.iterdir() if file.is_file()]
        return {"files": files}
    except Exception as e:
        logger.error(f"Could not list files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Could not list files: {str(e)}")

@router.get("/files/")
def list_files(current_user: UserDB = Depends(get_current_user)):
    """Returns a list of uploaded files (Authenticated Users Only)."""
    ensure_upload_dir()

    try:
        files = [file.name for file in UPLOAD_DIR.iterdir() if file.is_file()]
        logger.info(f"User {current_user.id} listed files")
        return {"files": files}
    except Exception as e:
        logger.error(f"Could not list files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Could not list files: {str(e)}")


@router.delete("/delete/{filename}")
def delete_file(
    filename: str,
    current_user: UserDB = Depends(get_current_user)  # Requires authentication
):
    """Delete an uploaded file (Authenticated Users Only)."""
    ensure_upload_dir()

    file_path = validate_and_sanitize_filename(filename)

    if not file_path.exists() or not file_path.is_file():
        logger.warning(f"User {current_user.id} attempted to delete non-existent file: {file_path}")
        raise HTTPException(status_code=404, detail="File not found")

    try:
        file_path.unlink()
        logger.info(f"User {current_user.id} deleted file: {file_path}")
        return {"detail": f"File {filename} deleted successfully"}
    except Exception as e:
        logger.error(f"Failed to delete file {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Could not delete file: {str(e)}")
