"""
Pydantic models for CIMR Claims Automation v1 API
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class ClaimCategory(str, Enum):
    """Claim categories"""
    PAYMENT = "Payment"
    AFFILIATION = "Affiliation"
    CONTRIBUTION = "Contribution"
    DEATH = "Death"
    TECHNICAL = "Technical"


class ClaimStatus(str, Enum):
    """Claim statuses"""
    NEW = "New"
    IN_PROGRESS = "In progress"
    RESOLVED = "Resolved"


class ClaimChannel(str, Enum):
    """Claim channels"""
    WEB = "Web"
    EMAIL = "Email"  # For backward compatibility with existing data


class ClaimSubmission(BaseModel):
    """Model for claim submission"""
    member_name: str = Field(..., description="Member's full name")
    member_id: str = Field(..., description="CIN or member ID")
    channel: ClaimChannel = Field(..., description="Submission channel")
    message: str = Field(..., description="Claim description")
    attachment_url: Optional[str] = Field(None, description="URL to attached document")


class ClaimResponse(BaseModel):
    """Model for claim response"""
    ticket_id: str = Field(..., description="Unique ticket identifier")
    member_name: str = Field(..., description="Member's full name")
    member_id: str = Field(..., description="CIN or member ID")
    channel: ClaimChannel = Field(..., description="Submission channel")
    message: str = Field(..., description="Claim description")
    attachment_url: Optional[str] = Field(None, description="URL to attached document")
    category: Optional[ClaimCategory] = Field(None, description="Claim category")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="AI classification confidence")
    priority: Optional[int] = Field(None, ge=1, le=5, description="Priority score 1-5")
    sla_hours: Optional[int] = Field(None, description="SLA deadline in hours")
    status: ClaimStatus = Field(..., description="Claim status")
    assigned_agent: Optional[str] = Field(None, description="Assigned internal agent")
    requires_attention: Optional[bool] = Field(None, description="Requires immediate attention")
    draft_response: Optional[str] = Field(None, description="AI-generated response draft")
    response_quality_score: Optional[float] = Field(None, ge=0, le=1, description="Response quality score")
    response_language: Optional[str] = Field(None, description="Response language")
    created_at: datetime = Field(..., description="Creation timestamp")
    last_updated: datetime = Field(..., description="Last update timestamp")


class StatusUpdateRequest(BaseModel):
    """Model for status update request"""
    status: str = Field(..., description="New status")
    assigned_agent: Optional[str] = Field(None, description="Assigned agent")
    notes: Optional[str] = Field(None, description="Update notes")


class APIResponse(BaseModel):
    """Standard API response model"""
    success: bool = Field(..., description="Request success status")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
