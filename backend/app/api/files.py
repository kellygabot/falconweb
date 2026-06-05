from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.db.postgres import get_db

router = APIRouter()


@router.post("/upload/{subject_id}")
async def upload_course_file(subject_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    # TODO: Instructor uploads PDF/PPT to subject
    # Store in MongoDB GridFS, save metadata in PostgreSQL
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.get("/download/{file_id}")
async def download_file(file_id: str, db: Session = Depends(get_db)):
    # TODO: Student downloads file from MongoDB GridFS
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.get("/subject/{subject_id}")
async def list_subject_files(subject_id: str, db: Session = Depends(get_db)):
    # TODO: List all files for a subject
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")
