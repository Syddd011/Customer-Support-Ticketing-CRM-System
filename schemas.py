"""
schemas.py
Pydantic models for request validation and response serialisation.
"""

from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime


# ---------------------------------------------------------------------------
# Shared / re-used types
# ---------------------------------------------------------------------------

VALID_STATUSES = {"Open", "In Progress", "Closed"}


# ---------------------------------------------------------------------------
# Request bodies
# ---------------------------------------------------------------------------

class TicketCreate(BaseModel):
    """Body for POST /api/tickets"""
    customer_name: str
    customer_email: EmailStr
    subject: str
    description: str

    @field_validator("customer_name", "subject", "description")
    @classmethod
    def must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Field must not be blank.")
        return v.strip()


class TicketUpdate(BaseModel):
    """Body for PUT /api/tickets/{ticket_id}"""
    status: Optional[str] = None
    note: Optional[str] = None          # a single note added on update

    @field_validator("status")
    @classmethod
    def status_must_be_valid(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_STATUSES:
            raise ValueError(f"status must be one of: {', '.join(VALID_STATUSES)}")
        return v


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------

class NoteOut(BaseModel):
    id: int
    ticket_id: str
    note_text: str
    created_at: str

    model_config = {"from_attributes": True}


class TicketSummary(BaseModel):
    """Used in the list endpoint — no description or notes to keep it lean."""
    ticket_id: str
    customer_name: str
    customer_email: str
    subject: str
    status: str
    created_at: str

    model_config = {"from_attributes": True}


class TicketDetail(BaseModel):
    """Full ticket with notes — used in the detail endpoint."""
    ticket_id: str
    customer_name: str
    customer_email: str
    subject: str
    description: str
    status: str
    created_at: str
    updated_at: str
    notes: List[NoteOut] = []

    model_config = {"from_attributes": True}


class TicketCreatedResponse(BaseModel):
    ticket_id: str
    created_at: str


class TicketUpdatedResponse(BaseModel):
    success: bool = True
    updated_at: str
