from sqlalchemy import Column, String, Boolean, DateTime, Enum, Integer, Table, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.postgres import Base


class RoleEnum(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    SCHOOL_ADMIN = "school_admin"
    ADVISOR = "advisor"
    INSTRUCTOR = "instructor"
    STUDENT = "student"


# Association table for many-to-many relationship
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', String, ForeignKey('user.id'), primary_key=True),
    Column('role', String, ForeignKey('role.name'), primary_key=True)
)


class User(Base):
    __tablename__ = "user"

    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    roles = relationship("Role", secondary=user_roles, back_populates="users")


class Role(Base):
    __tablename__ = "role"

    name = Column(String, primary_key=True, index=True)
    description = Column(String)

    users = relationship("User", secondary=user_roles, back_populates="roles")
