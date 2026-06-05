from sqlalchemy import Column, String, Float, Integer, ForeignKey, DateTime
from datetime import datetime

from app.db.postgres import Base


class TransmutationTable(Base):
    __tablename__ = "transmutation_table"

    id = Column(String, primary_key=True, index=True)
    school_year_id = Column(String, ForeignKey("school_year.id"), index=True)
    name = Column(String)  # e.g., "Default SY 2025-2026"
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    entries = []  # Relationship would be TransmutationEntry


class TransmutationEntry(Base):
    __tablename__ = "transmutation_entry"

    id = Column(String, primary_key=True, index=True)
    table_id = Column(String, ForeignKey("transmutation_table.id"), index=True)
    raw_percentage_min = Column(Float)  # e.g., 90.0
    raw_percentage_max = Column(Float)  # e.g., 100.0
    transmuted_grade = Column(String)  # e.g., "95"
    order = Column(Integer)
