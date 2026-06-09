from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import date
import uuid

from app.db.postgres import get_db
from app.core.dependencies import get_current_user, has_role
from app.models.user import User
from app.models.grading import SchoolYear, GradingPeriod, Section, Subject, Enrollment, GradingPeriodTypeEnum

router = APIRouter()


class SchoolYearCreate(BaseModel):
    year: int  # e.g., 2025 for SY 2025-2026
    is_current: bool = False


class SchoolYearResponse(BaseModel):
    id: str
    year: int
    is_current: bool

    class Config:
        from_attributes = True


class GradingPeriodCreate(BaseModel):
    school_year_id: str
    name: str  # e.g., "Q1", "1st Semester"
    type: str  # "quarter", "semester", "midterm", "finals"
    order: int  # for sorting
    start_date: date
    end_date: date


class GradingPeriodResponse(BaseModel):
    id: str
    school_year_id: str
    name: str
    type: str
    order: int
    is_locked: bool
    start_date: date
    end_date: date

    class Config:
        from_attributes = True


class SectionCreate(BaseModel):
    school_year_id: str
    name: str  # e.g., "3-A"
    grade_level: int  # 7-12
    advisor_id: str


class SectionResponse(BaseModel):
    id: str
    school_year_id: str
    name: str
    grade_level: int
    advisor_id: str

    class Config:
        from_attributes = True


class SubjectCreate(BaseModel):
    section_id: str
    school_year_id: str
    name: str
    code: str
    instructor_id: str


class SubjectResponse(BaseModel):
    id: str
    section_id: str
    school_year_id: str
    name: str
    code: str
    instructor_id: str

    class Config:
        from_attributes = True


class EnrollmentCreate(BaseModel):
    student_id: str
    section_id: str


class EnrollmentResponse(BaseModel):
    id: str
    student_id: str
    section_id: str

    class Config:
        from_attributes = True


# School Year Endpoints

@router.post("/school-years", response_model=SchoolYearResponse)
async def create_school_year(
    data: SchoolYearCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_role(["super_admin"])),
):
    existing = db.query(SchoolYear).filter(SchoolYear.year == data.year).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"School year {data.year} already exists"
        )

    school_year = SchoolYear(
        id=str(uuid.uuid4()),
        year=data.year,
        is_current=data.is_current,
    )
    db.add(school_year)
    db.commit()
    db.refresh(school_year)

    return SchoolYearResponse.from_orm(school_year)


@router.get("/school-years")
async def list_school_years(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    years = db.query(SchoolYear).all()
    return [SchoolYearResponse.from_orm(y) for y in years]


# Grading Period Endpoints

@router.post("/grading-periods", response_model=GradingPeriodResponse)
async def create_grading_period(
    data: GradingPeriodCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_role(["super_admin", "school_admin"])),
):
    grading_period = GradingPeriod(
        id=str(uuid.uuid4()),
        school_year_id=data.school_year_id,
        name=data.name,
        type=data.type,
        order=data.order,
        start_date=data.start_date,
        end_date=data.end_date,
        is_locked=False,
    )
    db.add(grading_period)
    db.commit()
    db.refresh(grading_period)

    return GradingPeriodResponse.from_orm(grading_period)


@router.get("/grading-periods/{school_year_id}")
async def list_grading_periods(
    school_year_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    periods = db.query(GradingPeriod).filter(
        GradingPeriod.school_year_id == school_year_id
    ).order_by(GradingPeriod.order).all()

    return [GradingPeriodResponse.from_orm(p) for p in periods]


# Section Endpoints

@router.post("/sections", response_model=SectionResponse)
async def create_section(
    data: SectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_role(["super_admin", "school_admin"])),
):
    section = Section(
        id=str(uuid.uuid4()),
        school_year_id=data.school_year_id,
        name=data.name,
        grade_level=data.grade_level,
        advisor_id=data.advisor_id,
    )
    db.add(section)
    db.commit()
    db.refresh(section)

    return SectionResponse.from_orm(section)


@router.get("/sections/{school_year_id}")
async def list_sections(
    school_year_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sections = db.query(Section).filter(
        Section.school_year_id == school_year_id
    ).all()

    return [SectionResponse.from_orm(s) for s in sections]


# Subject Endpoints

@router.post("/subjects", response_model=SubjectResponse)
async def create_subject(
    data: SubjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_role(["super_admin", "school_admin"])),
):
    subject = Subject(
        id=str(uuid.uuid4()),
        section_id=data.section_id,
        school_year_id=data.school_year_id,
        name=data.name,
        code=data.code,
        instructor_id=data.instructor_id,
    )
    db.add(subject)
    db.commit()
    db.refresh(subject)

    return SubjectResponse.from_orm(subject)


@router.get("/subjects/{section_id}")
async def list_section_subjects(
    section_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    subjects = db.query(Subject).filter(Subject.section_id == section_id).all()
    return [SubjectResponse.from_orm(s) for s in subjects]


@router.get("/subjects-by-instructor/{instructor_id}")
async def list_instructor_subjects(
    instructor_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all subjects taught by a specific instructor."""
    subjects = db.query(Subject).filter(Subject.instructor_id == instructor_id).all()
    return [SubjectResponse.from_orm(s) for s in subjects]


# Enrollment Endpoints

@router.post("/enrollments", response_model=EnrollmentResponse)
async def enroll_student(
    data: EnrollmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_role(["super_admin", "school_admin"])),
):
    existing = db.query(Enrollment).filter(
        Enrollment.student_id == data.student_id,
        Enrollment.section_id == data.section_id,
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student already enrolled in this section"
        )

    enrollment = Enrollment(
        id=str(uuid.uuid4()),
        student_id=data.student_id,
        section_id=data.section_id,
    )
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)

    return EnrollmentResponse.from_orm(enrollment)


@router.get("/enrollments/{section_id}")
async def list_section_enrollments(
    section_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    enrollments = db.query(Enrollment).filter(
        Enrollment.section_id == section_id
    ).all()

    return [EnrollmentResponse.from_orm(e) for e in enrollments]


@router.delete("/enrollments/{enrollment_id}")
async def remove_enrollment(
    enrollment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_role(["super_admin", "school_admin"])),
):
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()

    if not enrollment:
        raise HTTPException(status_code=404, detail="Enrollment not found")

    db.delete(enrollment)
    db.commit()

    return {"status": "deleted", "enrollment_id": enrollment_id}
