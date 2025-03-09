from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import FileResponse
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
    file.file.seek(0)  # Reset file pointer for reading

    max_size_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
    if file_size > max_size_bytes:
        raise HTTPException(status_code=413, detail=f"File size exceeds {MAX_FILE_SIZE_MB}MB limit")

@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """Handles media file uploads securely with size validation."""
    ensure_upload_dir()

    # Validate file size before processing
    validate_file_size(file)

    # Securely get the filename
    filename = get_unique_filename(file.filename)
    file_location = UPLOAD_DIR / filename

    try:
        # Save the file in chunks to prevent memory overload
        with file_location.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"File uploaded successfully: {filename}")
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

@router.get("/media/{filename}")
def get_file(filename: str):
    """Serve uploaded files securely."""
    ensure_upload_dir()

    # Prevent directory traversal attack (../)
    safe_filename = Path(filename).name
    file_path = UPLOAD_DIR / safe_filename

    if not file_path.exists() or not file_path.is_file():
        logger.warning(f"File not found: {filename}")
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path)

@router.delete("/delete/{filename}")
def delete_file(filename: str):
    """Delete an uploaded file."""
    ensure_upload_dir()

    # Prevent directory traversal attack (../)
    safe_filename = Path(filename).name
    file_path = UPLOAD_DIR / safe_filename

    if not file_path.exists() or not file_path.is_file():
        logger.warning(f"Attempted to delete non-existent file: {filename}")
        raise HTTPException(status_code=404, detail="File not found")

    try:
        file_path.unlink()  # Delete the file
        logger.info(f"File deleted successfully: {filename}")
        return {"detail": f"File {filename} deleted successfully"}
    except Exception as e:
        logger.error(f"Failed to delete file {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Could not delete file: {str(e)}")
