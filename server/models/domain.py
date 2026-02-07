from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

class OwnerType(str, Enum):
    CLIENT = "CLIENT"
    PROVIDER = "PROVIDER"
    ADVISOR = "ADVISOR"

class RequestStatus(str, Enum):
    PENDING = "PENDING"
    WAITING = "WAITING"
    PARTIAL = "PARTIAL"
    INVALID = "INVALID"
    FULFILLED = "FULFILLED"
    ESCALATED = "ESCALATED"
    PAUSED = "PAUSED"
    CLOSED = "CLOSED"

class RequestPriority(str, Enum):
    STANDARD = "STANDARD"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class Client(BaseModel):
    id: UUID
    name: str
    email: str
    phone: Optional[str] = None

class Provider(BaseModel):
    id: UUID
    name: str
    email: str
    portal_url: Optional[str] = None
    standard_response_days: int = 10

class Case(BaseModel):
    id: UUID
    advisor_id: UUID
    client_id: UUID
    title: str
    status: str = "ACTIVE"
    created_at: datetime
    updated_at: datetime

class Request(BaseModel):
    id: UUID
    case_id: UUID
    title: str
    description: Optional[str] = None
    
    owner_type: OwnerType
    client_owner_id: Optional[UUID] = None
    provider_owner_id: Optional[UUID] = None
    
    status: RequestStatus = RequestStatus.PENDING
    priority: RequestPriority = RequestPriority.STANDARD
    
    created_at: datetime
    next_action_at: datetime
    last_action_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    
    upload_token: UUID
    upload_expires_at: Optional[datetime] = None

class ActionAttempt(BaseModel):
    """Represents a proposed action by the Policy Engine"""
    action_type: str  # EMAIL_REMINDER, ESCALATE, etc.
    request_id: UUID
    reason: str
    metadata: Dict[str, Any] = {}
