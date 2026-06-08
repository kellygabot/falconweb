from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date
import uuid

from app.db.postgres import get_db
from app.db.mongo import get_mongo_db
from app.models.grading import Attendance, Subject, Enrollment, AttendanceStatusEnum
from app.core.audit import AuditLog

router = APIRouter()


class AttendanceRecord(BaseModel):
    student_id: str
    status: str  # present, absent, late, excused
    date: date


class BulkAttendanceRequest(BaseModel):
    records: list[AttendanceRecord]
    marked_by: str


@router.post("/mark-section/{section_id}")
async def mark_section_attendance(
    section_id: str,
    date: date,
    status: str,
    marked_by: str,
    db: Session = Depends(get_db),
    mongo_db = Depends(get_mongo_db),
):
    """
    Advisor marks attendance for entire section on a date.
    Pre-fills all subjects for that section on that date.
    """
    # Get all subjects for this section
    subjects = db.query(Subject).filter(Subject.section_id == section_id).all()

    if not subjects:
        raise HTTPException(status_code=404, detail="Section not found")

    # Get all students enrolled in this section
    enrollments = db.query(Enrollment).filter(
        Enrollment.section_id == section_id
    ).all()

    audit = AuditLog(mongo_db)

    # Mark attendance for each student in each subject
    for enrollment in enrollments:
        for subject in subjects:
            existing = db.query(Attendance).filter(
                Attendance.student_id == enrollment.student_id,
                Attendance.subject_id == subject.id,
                Attendance.date == date,
            ).first()

            if existing:
                before_status = existing.status
                existing.status = status
            else:
                new_record = Attendance(
                    id=str(uuid.uuid4()),
                    student_id=enrollment.student_id,
                    subject_id=subject.id,
                    date=date,
                    status=status,
                    marked_by=marked_by,
                )
                db.add(new_record)
                before_status = None

            await audit.log_attendance_change(
                marked_by,
                enrollment.student_id,
                subject.id,
                str(date),
                before_status,
                status,
            )

    db.commit()

    return {
        "status": "success",
        "section_id": section_id,
        "date": str(date),
        "attendance_status": status,
        "students_marked": len(enrollments),
    }


@router.post("/mark-subject/{subject_id}")
async def mark_subject_attendance(
    subject_id: str,
    request: BulkAttendanceRequest,
    db: Session = Depends(get_db),
    mongo_db = Depends(get_mongo_db),
):
    """
    Instructor marks attendance for their subject.
    Can override advisor's section-wide attendance.
    """
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    audit = AuditLog(mongo_db)

    for record in request.records:
        # Validate student is enrolled
        enrollment = db.query(Enrollment).filter(
            Enrollment.student_id == record.student_id,
            Enrollment.section_id == subject.section_id,
        ).first()

        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Student {record.student_id} not enrolled in section"
            )

        existing = db.query(Attendance).filter(
            Attendance.student_id == record.student_id,
            Attendance.subject_id == subject_id,
            Attendance.date == record.date,
        ).first()

        if existing:
            before_status = existing.status
            existing.status = record.status
        else:
            new_record = Attendance(
                id=str(uuid.uuid4()),
                student_id=record.student_id,
                subject_id=subject_id,
                date=record.date,
                status=record.status,
                marked_by=request.marked_by,
            )
            db.add(new_record)
            before_status = None

        await audit.log_attendance_change(
            request.marked_by,
            record.student_id,
            subject_id,
            str(record.date),
            before_status,
            record.status,
        )

    db.commit()

    return {
        "status": "success",
        "subject_id": subject_id,
        "records_updated": len(request.records),
    }
