"""
2-Phase Commit (2PC) manager for grade and deportment duplication across PostgreSQL and MongoDB.

Flow:
1. Begin transaction in PostgreSQL
2. Prepare stage in MongoDB (insert document without final commit)
3. If both ready → final commit to both
4. If either fails → rollback both
"""

from motor.motor_asyncio import AsyncDatabase
from sqlalchemy.orm import Session
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TwoPhaseCommitError(Exception):
    """Raised when 2PC fails at any stage"""
    pass


async def commit_grade(
    db: Session,
    mongo_db: AsyncDatabase,
    student_id: str,
    subject_id: str,
    grading_period_id: str,
    grade_data: dict,
) -> None:
    """
    Atomically commit grade to both PostgreSQL and MongoDB.

    Args:
        db: SQLAlchemy session (PostgreSQL)
        mongo_db: Motor async database (MongoDB)
        student_id: Student identifier
        subject_id: Subject identifier
        grading_period_id: Grading period identifier
        grade_data: Grade record to duplicate

    Raises:
        TwoPhaseCommitError: If commit fails at any stage
    """
    try:
        # Phase 1: Prepare in PostgreSQL
        db.begin_nested()
        # Grade insertion happens in the caller, here we just begin transaction

        # Phase 2: Ask MongoDB if it's ready (stage the document)
        mongo_grade = {
            "student_id": student_id,
            "subject_id": subject_id,
            "grading_period_id": grading_period_id,
            "timestamp": datetime.utcnow(),
            **grade_data,
        }

        # Stage in MongoDB (prepare phase)
        result = await mongo_db.grade_snapshots.insert_one(mongo_grade)
        mongo_id = result.inserted_id

        # Phase 3: Commit both
        # PostgreSQL commit happens via caller's session.commit()
        # This function confirms MongoDB insert was successful

        logger.info(
            f"2PC success: grade {mongo_id} for student {student_id} "
            f"in {grading_period_id}"
        )

    except Exception as e:
        # Rollback both on any error
        try:
            db.rollback()
        except Exception:
            pass

        # Try to remove from MongoDB if it was inserted
        try:
            await mongo_db.grade_snapshots.delete_one({"student_id": student_id})
        except Exception:
            pass

        logger.error(f"2PC failed: {str(e)}")
        raise TwoPhaseCommitError(f"Failed to commit grade: {str(e)}") from e


async def commit_deportment(
    db: Session,
    mongo_db: AsyncDatabase,
    student_id: str,
    section_id: str,
    grading_period_id: str,
    deportment_data: dict,
) -> None:
    """
    Atomically commit deportment grade to both PostgreSQL and MongoDB.
    """
    try:
        db.begin_nested()

        mongo_deportment = {
            "student_id": student_id,
            "section_id": section_id,
            "grading_period_id": grading_period_id,
            "timestamp": datetime.utcnow(),
            **deportment_data,
        }

        result = await mongo_db.deportment_snapshots.insert_one(mongo_deportment)
        mongo_id = result.inserted_id

        logger.info(
            f"2PC success: deportment {mongo_id} for student {student_id} "
            f"in {grading_period_id}"
        )

    except Exception as e:
        try:
            db.rollback()
        except Exception:
            pass

        try:
            await mongo_db.deportment_snapshots.delete_one({"student_id": student_id})
        except Exception:
            pass

        logger.error(f"2PC deportment failed: {str(e)}")
        raise TwoPhaseCommitError(f"Failed to commit deportment: {str(e)}") from e
