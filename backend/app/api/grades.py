from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.postgres import get_db

router = APIRouter()


class GradeUpdate(BaseModel):
    student_id: str
    subject_id: str
    component_id: str
    score: float


@router.get("/sheet/{subject_id}")
async def get_grade_sheet(subject_id: str, grading_period_id: str, db: Session = Depends(get_db)):
    # TODO: Fetch grade sheet for a subject
    # Returns columns (components) and rows (students)
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.post("/update")
async def update_grade(grade: GradeUpdate, db: Session = Depends(get_db)):
    # TODO: Update a grade, trigger 2PC to MongoDB
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")


@router.post("/lock/{grading_period_id}")
async def lock_grading_period(grading_period_id: str, db: Session = Depends(get_db)):
    # TODO: Lock grades for a grading period
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented")
