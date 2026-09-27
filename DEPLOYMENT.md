# LANDSYNC AI — Deployment & Infrastructure Guide

> **SIH Problem Context**: SIH26018 — Smart Automation  
> **Team**: Void  
> **System Classification**: Intelligent Land Record Digitalisation, Consistency Validation, GIS & Provenance Platform  
> **Notice**: All data in this repository is 100% synthetic demonstration data. No live government database or land registry is connected.

---

## 1. Deployment Topology & Architecture

LANDSYNC AI is architected as a modular, containerized multi-tier system:

```mermaid
graph TD
    Client["Next.js Web Frontend (Port 3000)"]
    API["FastAPI Backend Service (Port 8000 / $PORT)"]
    DB[("PostgreSQL 16 + PostGIS 3.4 (Port 5432)")]
    Storage["Evidence Storage (Local FS / S3 Bucket)"]
    
    Client -->|REST / JSON API| API
    API -->|SQLAlchemy 2.x ORM| DB
    API -->|Content-Addressed SHA-256| Storage
```

---

## 2. Environment Configuration Reference

Create a `.env` file based on `.env.example`:

| Environment Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | Optional | SQLite fallback | PostgreSQL + PostGIS connection string (`postgresql+psycopg://user:pass@host:5432/dbname`) |
| `STORAGE_PROVIDER` | No | `local` | Storage engine: `local` (filesystem) or `s3` (Amazon S3 / MinIO / R2) |
| `LOCAL_STORAGE_ROOT` | No | `.landsync-storage` | Filesystem directory for content-addressed evidence store |
| `AWS_S3_BUCKET` | If `STORAGE_PROVIDER=s3` | `None` | Amazon S3 bucket name |
| `AWS_REGION` | If `STORAGE_PROVIDER=s3` | `us-east-1` | AWS region |
| `JWT_SECRET_KEY` | Recommended | Demo secret | Cryptographic HS256 secret for signing authentication tokens |
| `JWT_EXPIRATION_MINUTES` | No | `120` | Token validity duration in minutes |
| `DOCUMENT_PROVIDER` | No | `mock` | `mock` (deterministic demo extractions) or `pdf_text` (pypdf + regex) |
| `CORS_ORIGINS` | No | `http://localhost:3000` | Comma-delimited list of permitted CORS origins |
| `PORT` | No | `8000` | Port to bind FastAPI service (supports dynamic PaaS `$PORT`) |
| `NEXT_PUBLIC_API_URL` | No | `http://localhost:8000` | Base URL used by the Next.js frontend client |

---

## 3. Local Development Quickstart

### Prerequisites
- Python 3.11+ (tested on Python 3.12, 3.14)
- Node.js 18+ & npm
- Git

### Step 1: Clone Repository
```bash
git clone https://github.com/sheikhsajid69/SIH26018.git
cd SIH26018
```

### Step 2: Initialize Backend & Database
```bash
cd apps/api
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt

# Run database migrations and seed synthetic scenarios:
alembic upgrade head
python ../../scripts/seed_demo.py

# Launch FastAPI development server:
uvicorn landsync.main:app --reload --port 8000
```

Verify backend health at: [http://localhost:8000/health](http://localhost:8000/health)

### Step 3: Launch Next.js Frontend
In a separate terminal window:
```bash
cd apps/web
npm install
npm run dev
```

Open the application at: [http://localhost:3000](http://localhost:3000)

---

## 4. Production Deployment via Docker Compose

Docker Compose runs the entire stack (PostgreSQL + PostGIS, FastAPI, Next.js) in production configuration:

```bash
# Build and start all services in detached mode:
docker compose up --build -d

# Verify container health:
docker compose ps

# Inspect logs:
docker compose logs -f api
```

The database schema is initialized and seeded automatically during API startup via the FastAPI lifespan manager.

---

## 5. Cloud Deployment Guide (Render / Railway / AWS)

### Option A: Render.com Blueprint

1. **Database Service**:
   - Create a **PostgreSQL** instance on Render.
   - Run in the database console:
     ```sql
     CREATE EXTENSION IF NOT EXISTS postgis;
     ```
   - Copy the Internal Database URL (`postgresql://...`).

2. **Backend Web Service**:
   - Type: **Web Service**
   - Source: Connect GitHub repository `sheikhsajid69/SIH26018`
   - Root Directory: `apps/api`
   - Environment: **Docker**
   - Health Check Path: `/health/live`
   - Environment Variables:
     - `DATABASE_URL`: `postgresql+psycopg://...` (paste your Render DB URL, ensuring prefix `postgresql+psycopg://`)
     - `JWT_SECRET_KEY`: Generate a random 64-character hex string
     - `STORAGE_PROVIDER`: `local` (or `s3` with AWS credentials)
     - `CORS_ORIGINS`: `https://your-frontend-app.onrender.com`

3. **Frontend Web Service**:
   - Type: **Web Service**
   - Root Directory: `apps/web`
   - Environment: **Docker**
   - Environment Variables:
     - `NEXT_PUBLIC_API_URL`: `https://your-api-app.onrender.com`

---

## 6. Verification & Health Probes

| Endpoint | Method | Expected Output | Purpose |
|---|---|---|---|
| `/health` | GET | `{"status": "ok", "mode": "DEMO_SYNTHETIC_ONLY"}` | General platform status |
| `/health/live` | GET | `{"status": "alive"}` | Kubernetes / PaaS liveness probe |
| `/health/ready` | GET | `{"status": "ready", "database": "connected"}` | Database readiness check |
| `/api/v1/auth/demo` | GET | Available synthetic roles & tokens | Verification of auth sub-system |
| `/api/v1/parcels/demo-parcel` | GET | Cadastral record for Sy No 124/2 | Cadastral database check |
| `/api/v1/review-cases` | GET | Queue of discrepancy review cases | Human-in-the-loop review queue |

---

## 7. Institutional Notice & Synthetic Disclaimer

> **ADVISORY NOTICE**: LANDSYNC AI is an educational, research, and hackathon prototype developed for Smart India Hackathon 2026 (SIH26018, Team Void). It operates exclusively on synthetic demonstration records. It does not establish legal title, convey property rights, or supersede authorized government land administration registries.
