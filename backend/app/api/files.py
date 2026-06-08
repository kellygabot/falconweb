from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime
from bson import ObjectId
import uuid
import io

from app.db.postgres import get_db
from app.db.mongo import get_mongo_db
from app.models.grading import CourseFile, Subject

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".ppt", ".pptx"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


@router.post("/upload/{subject_id}")
async def upload_course_file(
    subject_id: str,
    file: UploadFile = File(...),
    uploaded_by: str = "",
    db: Session = Depends(get_db),
    mongo_db = Depends(get_mongo_db),
):
    """
    Instructor uploads PDF/PPT to subject.
    Stores file in MongoDB GridFS, metadata in PostgreSQL.
    """
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    # Validate file
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename"
        )

    # Get file extension
    file_ext = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Read file contents
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds {MAX_FILE_SIZE / 1024 / 1024}MB"
        )

    try:
        # Store file data in MongoDB files collection
        file_doc = {
            "filename": file.filename,
            "content_type": file.content_type,
            "data": contents,
            "size": len(contents),
            "uploaded_at": datetime.utcnow(),
        }
        result = await mongo_db.files.insert_one(file_doc)
        mongo_file_id = str(result.inserted_id)

        # Store metadata in PostgreSQL
        course_file = CourseFile(
            id=str(uuid.uuid4()),
            subject_id=subject_id,
            filename=file.filename,
            original_filename=file.filename,
            file_size=len(contents),
            uploaded_by=uploaded_by,
            mongo_file_id=mongo_file_id,
        )
        db.add(course_file)
        db.commit()
        db.refresh(course_file)

        return {
            "id": course_file.id,
            "filename": course_file.filename,
            "file_size": course_file.file_size,
            "mongo_file_id": mongo_file_id,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store file: {str(e)}"
        )


@router.get("/download/{file_id}")
async def download_file(
    file_id: str,
    db: Session = Depends(get_db),
    mongo_db = Depends(get_mongo_db),
):
    """
    Download file from MongoDB.
    """
    course_file = db.query(CourseFile).filter(CourseFile.id == file_id).first()
    if not course_file:
        raise HTTPException(status_code=404, detail="File not found")

    try:
        file_doc = await mongo_db.files.find_one(
            {"_id": ObjectId(course_file.mongo_file_id)}
        )

        if not file_doc:
            raise HTTPException(status_code=404, detail="File data not found")

        file_data = file_doc.get("data")
        if isinstance(file_data, str):
            file_data = file_data.encode()

        return StreamingResponse(
            io.BytesIO(file_data),
            media_type=file_doc.get("content_type", "application/octet-stream"),
            headers={"Content-Disposition": f"attachment; filename={course_file.filename}"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve file"
        )


@router.get("/subject/{subject_id}")
async def list_subject_files(
    subject_id: str,
    db: Session = Depends(get_db),
):
    """
    List all files for a subject.
    """
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    files = db.query(CourseFile).filter(CourseFile.subject_id == subject_id).all()

    return {
        "subject_id": subject_id,
        "subject_name": subject.name,
        "files": [
            {
                "id": f.id,
                "filename": f.original_filename,
                "file_size": f.file_size,
                "uploaded_by": f.uploaded_by,
                "created_at": f.created_at.isoformat() if f.created_at else None,
            }
            for f in files
        ]
    }


@router.delete("/delete/{file_id}")
async def delete_file(
    file_id: str,
    db: Session = Depends(get_db),
    mongo_db = Depends(get_mongo_db),
):
    """
    Delete a file from both PostgreSQL and MongoDB.
    """
    course_file = db.query(CourseFile).filter(CourseFile.id == file_id).first()
    if not course_file:
        raise HTTPException(status_code=404, detail="File not found")

    try:
        # Delete from MongoDB
        await mongo_db.files.delete_one(
            {"_id": ObjectId(course_file.mongo_file_id)}
        )

        # Delete metadata from PostgreSQL
        db.delete(course_file)
        db.commit()

        return {"status": "deleted", "file_id": file_id}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete file"
        )
