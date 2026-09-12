# LANDSYNC AI

AI-assisted document intelligence and consistency validation for land records. It is an interoperability layer, **not** a government database or a legal-title system.

## Initial assessment

The repository was empty: no frontend, backend, package lock, database setup, Docker setup, AI/GIS pipeline, or reusable components existed. The first implemented vertical slice is **demo login → secure upload → deterministic mock extraction → synthetic authority comparison → officer decision → audit event**.

All records and model results supplied by this build are explicitly **SYNTHETIC DEMO / MOCK**. No government system is contacted.

## Run locally

Prerequisites: Node 20+, Python 3.12+.

```powershell
cd apps/api
python -m pip install -r requirements.txt
uvicorn landsync.main:app --reload --port 8000
```

In another terminal:

```powershell
cd apps/web
npm install
npm run dev
```

Open `http://localhost:3000`. API docs are at `http://localhost:8000/docs`. Demo API Bearer tokens: `demo-citizen`, `demo-officer`, and `demo-admin`.

## Checks

```powershell
python -m unittest discover -s apps/api/tests
cd apps/web; npm run build
```

## Persistence

`docker compose up --build` starts PostGIS, applies `infra/migrations/001_initial.sql` through the one-shot `migrate` service, then starts the web and API. The in-memory API is deliberately used only for this first demo slice, so it remains runnable before credentials and production storage are configured.

## Layout

- `apps/web` — Next.js citizen/officer demo console
- `apps/api` — FastAPI typed demo API and provider boundaries
- `apps/api/landsync/adapters/state` — state-authority adapter boundary
- `infra/migrations` — PostgreSQL/PostGIS schema migrations
- `data` — only controlled demo data belongs here
- root design/architecture documents — living project record
