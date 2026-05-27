# Customer Support Ticketing CRM

A full-stack web application built with **Python + FastAPI + SQLite + HTML/Tailwind CSS** for managing customer support tickets.

---

## Project Structure

```
crm/
├── main.py              # FastAPI application entry point
├── database.py          # SQLite connection & table initialisation
├── requirements.txt     # Python dependencies
├── crm.db               # SQLite database (auto-created on first run)
├── static/
│   ├── css/             # Custom CSS overrides
│   └── js/              # Frontend JavaScript
└── templates/           # Jinja2 HTML templates (coming next step)
```

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the server
```bash
uvicorn main:app --reload
```

The API will be live at **http://127.0.0.1:8000**

### 3. Health check
```
GET http://127.0.0.1:8000/
→ {"status": "CRM is running"}
```

### 4. Interactive API docs
```
http://127.0.0.1:8000/docs
```

---

## Database Schema

### tickets
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | Auto-increment |
| ticket_id | TEXT UNIQUE | Format: TKT-001 |
| customer_name | TEXT | |
| customer_email | TEXT | |
| subject | TEXT | |
| description | TEXT | |
| status | TEXT | Open / In Progress / Closed |
| created_at | TEXT | UTC datetime |
| updated_at | TEXT | UTC datetime |

### notes
| Column | Type | Notes |
|---|---|---|
| id | INTEGER PK | Auto-increment |
| ticket_id | TEXT FK | References tickets(ticket_id) |
| note_text | TEXT | |
| created_at | TEXT | UTC datetime |

---

## Environment

Create a `.env` file (see `.env.example`) for environment-specific settings.

---

## Deployment

Recommended: **Railway.app** (free tier, works great with FastAPI + SQLite)

```bash
# Procfile
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```
