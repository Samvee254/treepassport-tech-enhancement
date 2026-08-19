from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TreeCreate(BaseModel):
    tree_code: str
    species_id: Optional[int] = None
    county: Optional[str] = None
    gps_lat: Optional[float] = None
    gps_lng: Optional[float] = None
    planting_date: Optional[datetime] = None


class TreeUpdate(BaseModel):
    county: Optional[str] = None
    gps_lat: Optional[float] = None
    gps_lng: Optional[float] = None
    verification_status: Optional[str] = None
    species_id: Optional[int] = None


class TreeOut(BaseModel):
    id: int
    tree_code: str
    species_id: Optional[int]
    county: Optional[str]
    gps_lat: Optional[float]
    gps_lng: Optional[float]
    planting_date: Optional[datetime]
    verification_status: str
    current_health_status: str
    created_at: datetime

    class Config:
        from_attributes = True


class MonitoringRecordCreate(BaseModel):
    height_cm: Optional[float] = None
    health_status: str
    photo_url: Optional[str] = None
    notes: Optional[str] = None


class MonitoringRecordOut(BaseModel):
    id: int
    tree_id: int
    check_date: datetime
    height_cm: Optional[float]
    health_status: str
    photo_url: Optional[str]
    notes: Optional[str]

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str = "field_officer"


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
