"""
Audit log manager — tracks all changes to sensitive data (grades, attendance, deportment).
Stored in MongoDB for high-volume append-only access.
"""

from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AuditLog:
    def __init__(self, mongo_db):
        self.db = mongo_db
        self.collection = mongo_db.audit_logs

    async def log_grade_change(
        self,
        actor_id: str,
        student_id: str,
        subject_id: str,
        grading_period_id: str,
        component_id: str,
        before_value: float | None,
        after_value: float,
    ) -> None:
        """Log a grade entry or update."""
        entry = {
            "type": "grade",
            "actor_id": actor_id,
            "student_id": student_id,
            "subject_id": subject_id,
            "grading_period_id": grading_period_id,
            "component_id": component_id,
            "before": before_value,
            "after": after_value,
            "timestamp": datetime.utcnow(),
        }
        await self.collection.insert_one(entry)
        logger.info(f"Logged grade change: {entry}")

    async def log_attendance_change(
        self,
        actor_id: str,
        student_id: str,
        subject_id: str,
        date: str,
        before_status: str | None,
        after_status: str,
    ) -> None:
        """Log an attendance entry or update."""
        entry = {
            "type": "attendance",
            "actor_id": actor_id,
            "student_id": student_id,
            "subject_id": subject_id,
            "date": date,
            "before": before_status,
            "after": after_status,
            "timestamp": datetime.utcnow(),
        }
        await self.collection.insert_one(entry)
        logger.info(f"Logged attendance change: {entry}")

    async def log_deportment_change(
        self,
        actor_id: str,
        student_id: str,
        section_id: str,
        grading_period_id: str,
        before_grade: str | None,
        after_grade: str,
    ) -> None:
        """Log a deportment grade entry or update."""
        entry = {
            "type": "deportment",
            "actor_id": actor_id,
            "student_id": student_id,
            "section_id": section_id,
            "grading_period_id": grading_period_id,
            "before": before_grade,
            "after": after_grade,
            "timestamp": datetime.utcnow(),
        }
        await self.collection.insert_one(entry)
        logger.info(f"Logged deportment change: {entry}")

    async def log_lock_event(
        self,
        actor_id: str,
        grading_period_id: str,
        action: str,  # "lock" or "unlock"
    ) -> None:
        """Log a grading period lock/unlock."""
        entry = {
            "type": "lock_event",
            "actor_id": actor_id,
            "grading_period_id": grading_period_id,
            "action": action,
            "timestamp": datetime.utcnow(),
        }
        await self.collection.insert_one(entry)
        logger.info(f"Logged lock event: {entry}")

    async def get_logs(
        self,
        filter_dict: dict | None = None,
        limit: int = 100,
    ) -> list[dict]:
        """Fetch audit logs with optional filtering."""
        query = filter_dict or {}
        logs = await self.collection.find(query).sort("timestamp", -1).limit(limit).to_list(None)
        return logs
