from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional, Dict, Any


class TemporalCalculationStatus(SQLModel, table=True):
    __tablename__ = "temporal_calculation_status"
    
    calculation_id: str = Field(sa_column=Column(String, primary_key=True))
    workflow_id: str = Field(sa_column=Column(String, nullable=False))
    run_id: str = Field(sa_column=Column(String, nullable=False))
    project_id: int = Field(sa_column=Column(Integer, nullable=False))
    user_id: Optional[int] = Field(sa_column=Column(Integer, nullable=True))
    status: str = Field(default="queued", sa_column=Column(String, nullable=False))
    progress: int = Field(default=0, sa_column=Column(Integer))
    message: Optional[str] = Field(sa_column=Column(Text, nullable=True))
    result_data: Optional[Dict[str, Any]] = Field(sa_column=Column(JSONB, nullable=True))
    error_message: Optional[str] = Field(sa_column=Column(Text, nullable=True))
    created_at: Optional[datetime] = Field(sa_column=Column(DateTime, default=datetime.utcnow))
    updated_at: Optional[datetime] = Field(sa_column=Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow))