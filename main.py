# main.py - FastAPI app setup and page routes

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager

from database import init_db
from routers import tickets as tickets_router


# lifespan runs on startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server starting...")
    init_db()
    print("Database ready.")
    yield
    print("Server shutting down.")


# app setup
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

# API routes
app.include_router(tickets_router.router)


# HTML routes

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home(request: Request):
    """Show the ticket list page."""
    return templates.TemplateResponse(request, "index.html")


@app.get("/tickets/new", response_class=HTMLResponse, include_in_schema=False)
async def new_ticket_page(request: Request):
    """Show the create ticket form."""
    return templates.TemplateResponse(request, "create.html")


@app.get("/tickets/{ticket_id}", response_class=HTMLResponse, include_in_schema=False)
async def ticket_detail_page(request: Request, ticket_id: str):
    """Show the detail page for a single ticket."""
    return templates.TemplateResponse(
        request, "ticket_detail.html", {"ticket_id": ticket_id}
    )


# health check
@app.get("/health", tags=["Health"])
async def health():
    return {"status": "CRM is running"}
