from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Boolean, Enum, Date
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.postgres import Base


class GradingPeriodTypeEnum(str, enum.Enum):
    QUARTER = "quarter"
    SEMESTER = "semester"
    MIDTERM = "midterm"
    FINALS = "finals"


class AttendanceStatusEnum(str, enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"


class SchoolYear(Base):
    __tablename__ = "school_year"

    id = Column(String, primary_key=True, index=True)
    year = Column(Integer, unique=True, index=True)  # e.g., 2025 for SY 2025-2026
    is_current = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    grading_periods = relationship("GradingPeriod", back_populates="school_year")
    sections = relationship("Section", back_populates="school_year")


class GradingPeriod(Base):
    __tablename__ = "grading_period"

    id = Column(String, primary_key=True, index=True)
    school_year_id = Column(String, ForeignKey("school_year.id"), index=True)
    name = Column(String)  # e.g., "Q1", "1st Semester", "Midterm"
    type = Column(Enum(GradingPeriodTypeEnum))
    order = Column(Integer)  # For sorting quarters/semesters
    is_locked = Column(Boolean, default=False)
    start_date = Column(Date)
    end_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)

    school_year = relationship("SchoolYear", back_populates="grading_periods")
    grades = relationship("Grade", back_populates="grading_period")


class Section(Base):
    __tablename__ = "section"

    id = Column(String, primary_key=True, index=True)
    school_year_id = Column(String, ForeignKey("school_year.id"), index=True)
    name = Column(String, index=True)  # e.g., "3-A"
    grade_level = Column(Integer)  # 7, 8, 9, 10, 11, 12
    advisor_id = Column(String, ForeignKey("user.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    school_year = relationship("SchoolYear", back_populates="sections")
    enrollments = relationship("Enrollment", back_populates="section")
    subjects = relationship("Subject", back_populates="section")


class Subject(Base):
    __tablename__ = "subject"

    id = Column(String, primary_key=True, index=True)
    section_id = Column(String, ForeignKey("section.id"), index=True)
    school_year_id = Column(String, ForeignKey("school_year.id"), index=True)
    name = Column(String)  # e.g., "Mathematics"
    code = Column(String)
    instructor_id = Column(String, ForeignKey("user.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    section = relationship("Section", back_populates="subjects")
    grade_components = relationship("GradeComponent", back_populates="subject")
    grades = relationship("Grade", back_populates="subject")
    files = relationship("CourseFile", back_populates="subject")


class Enrollment(Base):
    __tablename__ = "enrollment"

    id = Column(String, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("user.id"), index=True)
    section_id = Column(String, ForeignKey("section.id"), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    section = relationship("Section", back_populates="enrollments")


class GradeComponent(Base):
    __tablename__ = "grade_component"

    id = Column(String, primary_key=True, index=True)
    subject_id = Column(String, ForeignKey("subject.id"), index=True)
    name = Column(String)  # e.g., "Quiz 1", "Midterm Exam"
    component_type = Column(String)  # "quiz", "exam", "activity"
    weight = Column(Float)  # 0-100, must sum to 100 per subject
    order = Column(Integer)  # Display order
    created_at = Column(DateTime, default=datetime.utcnow)

    subject = relationship("Subject", back_populates="grade_components")
    grades = relationship("Grade", back_populates="component")


class Grade(Base):
    __tablename__ = "grade"

    id = Column(String, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("user.id"), index=True)
    subject_id = Column(String, ForeignKey("subject.id"), index=True)
    grading_period_id = Column(String, ForeignKey("grading_period.id"), index=True)
    component_id = Column(String, ForeignKey("grade_component.id"), index=True)
    score = Column(Float, nullable=True)  # Raw score (e.g., 78 out of 100)
    entered_by = Column(String, ForeignKey("user.id"))  # Who entered this grade
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    subject = relationship("Subject", back_populates="grades")
    grading_period = relationship("GradingPeriod", back_populates="grades")
    component = relationship("GradeComponent", back_populates="grades")


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(String, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("user.id"), index=True)
    subject_id = Column(String, ForeignKey("subject.id"), index=True)
    date = Column(Date, index=True)
    status = Column(Enum(AttendanceStatusEnum))
    marked_by = Column(String, ForeignKey("user.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DeportmentGrade(Base):
    __tablename__ = "deportment_grade"

    id = Column(String, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("user.id"), index=True)
    section_id = Column(String, ForeignKey("section.id"), index=True)
    grading_period_id = Column(String, ForeignKey("grading_period.id"), index=True)
    grade = Column(String)  # Letter grade: A, B, C, D, F
    entered_by = Column(String, ForeignKey("user.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CourseFile(Base):
    __tablename__ = "course_file"

    id = Column(String, primary_key=True, index=True)
    subject_id = Column(String, ForeignKey("subject.id"), index=True)
    filename = Column(String)
    original_filename = Column(String)
    file_size = Column(Integer)
    uploaded_by = Column(String, ForeignKey("user.id"))
    mongo_file_id = Column(String)  # Reference to GridFS file ID
    created_at = Column(DateTime, default=datetime.utcnow)

    subject = relationship("Subject", back_populates="files")
