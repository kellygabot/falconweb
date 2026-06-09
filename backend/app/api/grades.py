from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
import uuid

from app.db.postgres import get_db
from app.db.mongo import get_mongo_db
from app.models.grading import (
    Grade, GradeComponent, GradingPeriod, Subject, Enrollment, Attendance
)
from app.core.audit import AuditLog
from app.core.two_phase_commit import commit_grade, TwoPhaseCommitError

router = APIRouter()


class GradeUpdate(BaseModel):
    student_id: str
    subject_id: str
    component_id: str
    score: float
    entered_by: str


class GradeSheetRow(BaseModel):
    student_id: str
    student_name: str
    grades: dict[str, float | None]  # component_id -> score


class GradeSheetResponse(BaseModel):
    subject_id: str
    subject_name: str
    grading_period_id: str
    is_locked: bool
    components: list[dict]  # [{id, name, weight, order}]
    students: list[GradeSheetRow]


@router.get("/sheet/{subject_id}")
async def get_grade_sheet(
    subject_id: str,
    grading_period_id: str,
    db: Session = Depends(get_db),
):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    grading_period = db.query(GradingPeriod).filter(
        GradingPeriod.id == grading_period_id
    ).first()
    if not grading_period:
        raise HTTPException(status_code=404, detail="Grading period not found")

    # Get grade components
    components = db.query(GradeComponent).filter(
        GradeComponent.subject_id == subject_id
    ).order_by(GradeComponent.order).all()

    # Get enrolled students with their user data
    from app.models.user import User
    enrollments = db.query(Enrollment).join(User).filter(
        Enrollment.section_id == subject.section_id
    ).all()

    # Build grade sheet rows
    students = []
    for enrollment in enrollments:
        student_user = db.query(User).filter(User.id == enrollment.student_id).first()
        grades_dict = {}
        for component in components:
            grade = db.query(Grade).filter(
                Grade.student_id == enrollment.student_id,
                Grade.subject_id == subject_id,
                Grade.component_id == component.id,
                Grade.grading_period_id == grading_period_id,
            ).first()
            grades_dict[component.id] = grade.score if grade else None

        student_name = ""
        if student_user:
            student_name = f"{student_user.first_name} {student_user.last_name}"

        students.append(GradeSheetRow(
            student_id=enrollment.student_id,
            student_name=student_name,
            grades=grades_dict,
        ))

    return GradeSheetResponse(
        subject_id=subject_id,
        subject_name=subject.name,
        grading_period_id=grading_period_id,
        is_locked=grading_period.is_locked,
        components=[
            {
                "id": c.id,
                "name": c.name,
                "weight": c.weight,
                "order": c.order,
            }
            for c in components
        ],
        students=students,
    )


@router.post("/update")
async def update_grade(
    grade: GradeUpdate,
    db: Session = Depends(get_db),
    mongo_db = Depends(get_mongo_db),
):
    # Check if grading period is locked
    subject = db.query(Subject).filter(Subject.id == grade.subject_id).first()
    grading_periods = db.query(GradingPeriod).filter(
        GradingPeriod.is_locked == True,
        GradingPeriod.school_year_id == subject.school_year_id,
    ).all()

    if any(gp.id for gp in grading_periods):  # TODO: Better logic
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Grading period is locked"
        )

    # Get existing grade or create new
    existing_grade = db.query(Grade).filter(
        Grade.student_id == grade.student_id,
        Grade.subject_id == grade.subject_id,
        Grade.component_id == grade.component_id,
    ).first()

    before_value = existing_grade.score if existing_grade else None

    try:
        if existing_grade:
            existing_grade.score = grade.score
            existing_grade.updated_at = datetime.utcnow()
        else:
            new_grade = Grade(
                id=str(uuid.uuid4()),
                student_id=grade.student_id,
                subject_id=grade.subject_id,
                component_id=grade.component_id,
                grading_period_id="",  # TODO: Extract from request
                score=grade.score,
                entered_by=grade.entered_by,
            )
            db.add(new_grade)

        db.flush()

        # Trigger 2PC to MongoDB
        await commit_grade(
            db, mongo_db,
            grade.student_id,
            grade.subject_id,
            "",  # TODO: grading_period_id
            {"score": grade.score, "component_id": grade.component_id},
        )

        db.commit()

        # Log the change
        audit = AuditLog(mongo_db)
        await audit.log_grade_change(
            grade.entered_by,
            grade.student_id,
            grade.subject_id,
            "",  # TODO: grading_period_id
            grade.component_id,
            before_value,
            grade.score,
        )

        return {"status": "success", "score": grade.score}

    except TwoPhaseCommitError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save grade: {str(e)}"
        )


@router.post("/lock/{grading_period_id}")
async def lock_grading_period(
    grading_period_id: str,
    actor_id: str,
    db: Session = Depends(get_db),
    mongo_db = Depends(get_mongo_db),
):
    grading_period = db.query(GradingPeriod).filter(
        GradingPeriod.id == grading_period_id
    ).first()

    if not grading_period:
        raise HTTPException(status_code=404, detail="Grading period not found")

    grading_period.is_locked = True
    db.commit()

    # Log the lock event
    audit = AuditLog(mongo_db)
    await audit.log_lock_event(actor_id, grading_period_id, "lock")

    return {"status": "locked", "grading_period_id": grading_period_id}


@router.post("/unlock/{grading_period_id}")
async def unlock_grading_period(
    grading_period_id: str,
    actor_id: str,
    db: Session = Depends(get_db),
    mongo_db = Depends(get_mongo_db),
):
    grading_period = db.query(GradingPeriod).filter(
        GradingPeriod.id == grading_period_id
    ).first()

    if not grading_period:
        raise HTTPException(status_code=404, detail="Grading period not found")

    grading_period.is_locked = False
    db.commit()

    # Log the unlock event
    audit = AuditLog(mongo_db)
    await audit.log_lock_event(actor_id, grading_period_id, "unlock")

    return {"status": "unlocked", "grading_period_id": grading_period_id}
