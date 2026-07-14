from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from app.api.deps import get_current_user, require_admin
from app.utils.file_validation import detect_file_type
from app.models.user import UserDB
from app.core.config import UPLOAD_FOLDER

import shutil
import os
import mimetypes
import logging
from pathlib import Path
import uuid

router = APIRouter()

# Configure logging
logger = logging.getLogger(__name__)

# Define the upload directory (shared with avatar uploads via config.UPLOAD_FOLDER)
UPLOAD_DIR = Path(UPLOAD_FOLDER)
MAX_FILE_SIZE_MB = 10  # Maximum allowed file size in MB
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".pdf", ".mp4"}
# Detected (magic-byte) MIME type -> canonical extension. The stored extension is
# always derived from the detected type, never from the client filename, so an
# attacker cannot save an HTML/script payload under a ".html" name.
MIME_TO_EXT = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "application/pdf": ".pdf",
    "video/mp4": ".mp4",
}
ALLOWED_MIME_TYPES = set(MIME_TO_EXT)
# Content types safe to render inline in the browser. Anything else is served as a
# download so a mislabeled upload can never execute as HTML/script on our origin.
INLINE_SAFE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}

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

def validate_and_sanitize_filename(filename: str) -> Path:
    """Sanitize and return a safe file path within the upload directory."""
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

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail=f"File size exceeds {MAX_FILE_SIZE_MB}MB limit")

    # Trust the bytes, not the declared content-type/extension; the stored name is
    # a random uuid plus the extension implied by the detected type.
    detected = detect_file_type(contents)
    if detected not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="File content does not match an allowed type")

    filename = f"{uuid.uuid4().hex}{MIME_TO_EXT[detected]}"
    file_location = UPLOAD_DIR / filename
    try:
        with file_location.open("wb") as buffer:
            buffer.write(contents)
        logger.info(f"User {current_user.id} uploaded file: {file_location}")
    except Exception as e:
        logger.error(f"File upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail="File upload failed")

    return {"filename": filename, "url": f"/media/{filename}"}


@router.get("/files/")
def list_files(current_user: UserDB = Depends(require_admin)):
    """Returns a list of uploaded files (admins only)."""
    ensure_upload_dir()

    try:
        files = [file.name for file in UPLOAD_DIR.iterdir() if file.is_file()]
        return {"files": files}
    except Exception as e:
        logger.error(f"Could not list files: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not list files")

@router.delete("/delete/{filename}")
def delete_file(
    filename: str,
    current_user: UserDB = Depends(require_admin)  # Admins only
):
    """Delete an uploaded file (admins only)."""
    ensure_upload_dir()

    file_path = validate_and_sanitize_filename(filename)

    if not file_path.exists() or not file_path.is_file():
        logger.warning(f"Admin {current_user.id} attempted to delete non-existent file: {file_path}")
        raise HTTPException(status_code=404, detail="File not found")

    try:
        file_path.unlink()
        logger.info(f"Admin {current_user.id} deleted file: {file_path}")
        return {"detail": f"File {filename} deleted successfully"}
    except Exception as e:
        logger.error(f"Failed to delete file {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not delete file")


@router.get("/{filename}")
def serve_file(filename: str):
    """Serve an uploaded media file (public).

    Only known-safe image types are served inline; anything else is forced to a
    download with a generic content type, so a mislabeled upload can never be
    interpreted as HTML/script on our origin (regardless of its extension).
    """
    file_path = validate_and_sanitize_filename(filename)
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    guessed, _ = mimetypes.guess_type(str(file_path))
    if guessed in INLINE_SAFE_TYPES:
        media_type = guessed
        disposition = "inline"
    else:
        media_type = "application/octet-stream"
        disposition = "attachment"
    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        headers={"Content-Disposition": f'{disposition}; filename="{file_path.name}"'},
    )
