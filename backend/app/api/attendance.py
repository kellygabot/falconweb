from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date

from app.db.postgres import get_db

router = APIRouter()


class AttendanceUpdate(BaseModel):
    student_id: str
    status: str  # present, absent, late, excused
    date: date


@router.post("/mark-section/{section_id}")
async def mark_section_attendance(section_id: str, grading_period_id: str, date: date, status: str, db: Session = Depends(get_db)):
    # TODO: Advisor marks attendance for entire section
    # This pre-fills all subjects for that section on that date
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.post("/mark-subject/{subject_id}")
async def mark_subject_attendance(subject_id: str, attendance: AttendanceUpdate, db: Session = Depends(get_db)):
    # TODO: Instructor marks attendance for their subject
    # Can override advisor's section-wide attendance
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")
