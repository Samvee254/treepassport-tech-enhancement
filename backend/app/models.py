from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="field_officer")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Species(Base):
    __tablename__ = "species"

    id = Column(Integer, primary_key=True, index=True)
    common_name = Column(String, nullable=False)
    scientific_name = Column(String)
    expected_growth_rate_cm_per_month = Column(Float, nullable=False)


class Tree(Base):
    __tablename__ = "trees"

    id = Column(Integer, primary_key=True, index=True)
    tree_code = Column(String, unique=True, nullable=False, index=True)
    species_id = Column(Integer, ForeignKey("species.id"))
    county = Column(String)
    gps_lat = Column(Float)
    gps_lng = Column(Float)
    planting_date = Column(DateTime)
    verification_status = Column(String, default="pending")
    current_health_status = Column(String, default="healthy")
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    species = relationship("Species")
    monitoring_records = relationship("MonitoringRecord", back_populates="tree")


class MonitoringRecord(Base):
    __tablename__ = "monitoring_records"

    id = Column(Integer, primary_key=True, index=True)
    tree_id = Column(Integer, ForeignKey("trees.id"), nullable=False)
    checked_by = Column(Integer, ForeignKey("users.id"))
    check_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    height_cm = Column(Float)
    health_status = Column(String)
    photo_url = Column(String)
    notes = Column(String)

    tree = relationship("Tree", back_populates="monitoring_records")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    tree_id = Column(Integer, ForeignKey("trees.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    field_changed = Column(String)
    old_value = Column(String)
    new_value = Column(String)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    action_type = Column(String)
    flagged = Column(Boolean, default=False)
