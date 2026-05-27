"""
main.py
FastAPI entry point for the Customer Support Ticketing CRM.
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager

from database import init_db
from routers import tickets as tickets_router


# ---------------------------------------------------------------------------
# Lifespan: runs once on startup and once on shutdown
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[main] Starting CRM server ...")
    init_db()
    print("[main] Database ready.")
    yield
    print("[main] Shutting down CRM server.")


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Customer Support Ticketing CRM",
    description="A simple, full-stack support ticket management system.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files + Jinja2 templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ---------------------------------------------------------------------------
# Routers (API)
# ---------------------------------------------------------------------------
app.include_router(tickets_router.router)


# ---------------------------------------------------------------------------
# HTML Page Routes
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home(request: Request):
    """Home page — ticket list with search and filter."""
    return templates.TemplateResponse(request, "index.html")


@app.get("/tickets/new", response_class=HTMLResponse, include_in_schema=False)
async def new_ticket_page(request: Request):
    """New ticket creation form page."""
    return templates.TemplateResponse(request, "create.html")


@app.get("/tickets/{ticket_id}", response_class=HTMLResponse, include_in_schema=False)
async def ticket_detail_page(request: Request, ticket_id: str):
    """Ticket detail page — view, update status, add notes."""
    return templates.TemplateResponse(
        request, "ticket_detail.html", {"ticket_id": ticket_id}
    )


# ---------------------------------------------------------------------------
# Health check (JSON)
# ---------------------------------------------------------------------------
@app.get("/health", tags=["Health"])
async def health():
    return {"status": "CRM is running"}
