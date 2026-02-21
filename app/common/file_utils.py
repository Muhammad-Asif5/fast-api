import os
from fastapi import HTTPException, UploadFile, status
import uuid
from uuid import UUID
import shutil

UPLOAD_DIR = "uploads/employees"
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# -----------------------
# Handle Image
# -----------------------
def validate_image_file(file: UploadFile) -> None:
    """Validate uploaded image file"""
    if not file:
        return
    
    # Check file extension
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
        )
    
    # Check file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()  # Get position (file size)
    file.file.seek(0)  # Reset to beginning
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024)}MB"
        )
    
    # Validate MIME type
    content_type = file.content_type
    if content_type not in ['image/jpeg', 'image/png', 'image/gif', 'image/webp']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image format"
        )

# -----------------------
# Handle File Upload
# -----------------------
def save_uploaded_file(file: UploadFile) -> str:
    """Save uploaded file and return path"""
    # Ensure the uploads folder exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1].lower()
    filename = f"{uuid.uuid4()}{file_extension}"
    file_location = os.path.join(UPLOAD_DIR, filename)
    
    try:
        with open(file_location, "wb") as f:
            shutil.copyfileobj(file.file, f)
        return file_location
    except Exception as e:
        # Clean up if save fails
        if os.path.exists(file_location):
            os.remove(file_location)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
