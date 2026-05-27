"""
routers/tickets.py
All ticket-related API endpoints:

  POST   /api/tickets                 — create a new ticket
  GET    /api/tickets                 — list tickets (with search + status filter)
  GET    /api/tickets/{ticket_id}     — get full ticket detail + notes
  PUT    /api/tickets/{ticket_id}     — update status and/or add a note
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timezone
from typing import Optional, List

from database import get_connection, generate_ticket_id
from schemas import (
    TicketCreate,
    TicketUpdate,
    TicketSummary,
    TicketDetail,
    NoteOut,
    TicketCreatedResponse,
    TicketUpdatedResponse,
)

router = APIRouter(prefix="/api/tickets", tags=["Tickets"])


# ---------------------------------------------------------------------------
# Helper: fetch a ticket row by ticket_id (raises 404 if not found)
# ---------------------------------------------------------------------------

def _get_ticket_or_404(conn, ticket_id: str):
    row = conn.execute(
        "SELECT * FROM tickets WHERE ticket_id = ?", (ticket_id,)
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Ticket '{ticket_id}' not found.")
    return row


# ---------------------------------------------------------------------------
# Helper: fetch all notes for a ticket
# ---------------------------------------------------------------------------

def _get_notes(conn, ticket_id: str) -> List[dict]:
    rows = conn.execute(
        "SELECT * FROM notes WHERE ticket_id = ? ORDER BY created_at ASC",
        (ticket_id,),
    ).fetchall()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# POST /api/tickets
# ---------------------------------------------------------------------------

@router.post("/", response_model=TicketCreatedResponse, status_code=201)
async def create_ticket(body: TicketCreate):
    """
    Create a new support ticket.
    Auto-generates a unique ticket_id in the format TKT-001.
    """
    ticket_id = generate_ticket_id()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO tickets
                (ticket_id, customer_name, customer_email, subject, description,
                 status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, 'Open', ?, ?)
            """,
            (
                ticket_id,
                body.customer_name,
                body.customer_email,
                body.subject,
                body.description,
                now,
                now,
            ),
        )
        conn.commit()

    return TicketCreatedResponse(ticket_id=ticket_id, created_at=now)


# ---------------------------------------------------------------------------
# GET /api/tickets
# ---------------------------------------------------------------------------

@router.get("/", response_model=List[TicketSummary])
async def list_tickets(
    status: Optional[str] = Query(
        default=None,
        description="Filter by status: Open | In Progress | Closed",
    ),
    search: Optional[str] = Query(
        default=None,
        description="Search across ticket_id, customer_name, customer_email, subject",
    ),
):
    """
    Return all tickets, optionally filtered by status and/or a search term.
    Results are ordered newest-first.
    """
    query = "SELECT * FROM tickets WHERE 1=1"
    params: list = []

    if status:
        query += " AND status = ?"
        params.append(status)

    if search:
        like = f"%{search}%"
        query += (
            " AND (ticket_id LIKE ? OR customer_name LIKE ?"
            " OR customer_email LIKE ? OR subject LIKE ?"
            " OR description LIKE ?)"
        )
        params.extend([like, like, like, like, like])

    query += " ORDER BY created_at DESC"

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()

    return [TicketSummary(**dict(r)) for r in rows]


# ---------------------------------------------------------------------------
# GET /api/tickets/{ticket_id}
# ---------------------------------------------------------------------------

@router.get("/{ticket_id}", response_model=TicketDetail)
async def get_ticket(ticket_id: str):
    """
    Return full details for a single ticket, including all its notes.
    """
    with get_connection() as conn:
        ticket = _get_ticket_or_404(conn, ticket_id)
        notes = _get_notes(conn, ticket_id)

    data = dict(ticket)
    data["notes"] = [NoteOut(**n) for n in notes]
    return TicketDetail(**data)


# ---------------------------------------------------------------------------
# PUT /api/tickets/{ticket_id}
# ---------------------------------------------------------------------------

@router.put("/{ticket_id}", response_model=TicketUpdatedResponse)
async def update_ticket(ticket_id: str, body: TicketUpdate):
    """
    Update a ticket's status and/or add a new note.
    At least one of status or note must be provided.
    """
    if body.status is None and (body.note is None or not body.note.strip()):
        raise HTTPException(
            status_code=422,
            detail="Provide at least one of: 'status' or 'note'.",
        )

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    with get_connection() as conn:
        # Verify the ticket exists before doing anything
        _get_ticket_or_404(conn, ticket_id)

        # Update status if provided
        if body.status is not None:
            conn.execute(
                "UPDATE tickets SET status = ?, updated_at = ? WHERE ticket_id = ?",
                (body.status, now, ticket_id),
            )

        # Add note if provided
        if body.note and body.note.strip():
            conn.execute(
                "INSERT INTO notes (ticket_id, note_text, created_at) VALUES (?, ?, ?)",
                (ticket_id, body.note.strip(), now),
            )
            # Always bump updated_at when a note is added too
            conn.execute(
                "UPDATE tickets SET updated_at = ? WHERE ticket_id = ?",
                (now, ticket_id),
            )

        conn.commit()

    return TicketUpdatedResponse(success=True, updated_at=now)
