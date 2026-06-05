# Falcon School — Grading & Management System

A modern, centralized platform for school grading, attendance tracking, student file management, and communication.

## Features

- **Faculty Grading System** — Excel-like grade sheet with configurable components, weights, and transmutation
- **Attendance Tracking** — Per-subject attendance with section-wide pre-fill capability
- **Student Portal** — View grades (raw scores only) and download course materials
- **Report Card Designer** — Canva-like template builder for official grade reports
- **Facebook Integration** — Display school announcements from both Facebook pages on the landing page
- **Audit Logging** — Complete history of all grade/attendance/deportment changes
- **Role-Based Access** — Super Admin, School Admin, Advisor, Instructor, and Student roles with context-aware permissions

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Next.js 16+ (TypeScript, Tailwind) |
| Backend | FastAPI (Python 3.11) with uv |
| Database | PostgreSQL (Supabase) + MongoDB Atlas |
| Auth | JWT-based |
| Deployment | Vercel (frontend), Railway (backend) |

## Quick Start

### Backend

```bash
cd backend

# Install dependencies
uv sync

# Create .env file from example
cp .env.example .env
# Edit .env with your Supabase and MongoDB credentials

# Run development server
uv run fastapi dev app/main.py
```

Backend API runs at `http://localhost:8000`

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend runs at `http://localhost:3000`

## Database Setup

You'll need to set up:

1. **Supabase PostgreSQL** — Create a new Supabase project
2. **MongoDB Atlas** — Create a cluster and database
3. Add their connection strings to `backend/.env`

The backend auto-creates tables on first run via SQLAlchemy.

## Project Documentation

See [CLAUDE.md](./CLAUDE.md) for:
- Detailed architecture and design decisions
- Database schema overview
- Common development tasks
- Deployment guide

## Development Workflow

1. **Create a feature branch**: `git checkout -b feature/your-feature`
2. **Make changes** to backend and/or frontend
3. **Test locally** with dev servers
4. **Commit and push**: Changes auto-deploy to Railway (backend) and Vercel (frontend)

## Key Concepts

### 2-Phase Commit (2PC)

Grades and deportment grades are duplicated across PostgreSQL and MongoDB for data integrity. The system uses 2PC to ensure both databases stay in sync:
- Prepare transaction in PostgreSQL
- Stage document in MongoDB
- Commit both or rollback both

### Role-Based Access

Roles stack — one person can be Super Admin + Advisor + Instructor simultaneously. Permissions are resolved by context (which page/action the user is on), not a single assigned role.

### Transmutation Table

School admins configure a transmutation table to convert raw percentage scores to letter grades. If not configured, raw percentages are displayed.

### Attendance & Deportment

- **Attendance**: Per subject, per day; advisors set section-wide, instructors override per subject
- **Deportment**: Per student, per quarter; entered by advisor or school admin

## Support

For issues or questions, refer to [CLAUDE.md](./CLAUDE.md) or contact the development team.
