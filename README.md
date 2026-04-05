# Gym Wear Backend (FastAPI + Prisma + Postgres + Redis)

Backend services for the gym-wear web application. Frontend lives separately. This repo wires FastAPI, PostgreSQL (via Prisma ORM), Redis caching, and a simple AI chat endpoint.

## Quick start (Dockerized Postgres + Redis)
```bash
cp .env.example .env
docker compose up -d  # starts Postgres (5442) and Redis (6380)

# in a virtualenv (Python 3.11 is recommended; Torch wheels aren't built for 3.14)
python3.11 -m venv .venv
source .venv/bin/activate
# Install Torch first (avoids wheel resolution issues on macOS)
pip install --index-url https://download.pytorch.org/whl/cpu torch==2.2.2
pip install -r requirements.txt
prisma generate          # builds the Prisma Python client
prisma migrate dev --name init  # creates schema in Postgres (interactive; rerun after schema changes)
python scripts/seed.py   # load sample catalog data

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## One-liner run (fresh checkout)
```bash
cp .env.example .env \
  && docker compose up -d \
  && python3.11 -m venv .venv \
  && source .venv/bin/activate \
  && pip install --index-url https://download.pytorch.org/whl/cpu torch==2.2.2 \
  && pip install -r requirements.txt \
  && prisma generate \
  && prisma migrate dev --name init \
  && python scripts/seed.py \
  && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Python & Torch notes
- Use Python 3.11 (Torch 2.2.2 does not have wheels for 3.14+ yet).
- On Apple Silicon, the CPU wheel via `--index-url https://download.pytorch.org/whl/cpu` is the safest default; switch to `--index-url https://download.pytorch.org/whl/nightly/cpu` only if you need a newer build.

## Running details
- Backend: FastAPI served by Uvicorn on port 8000.
- Database: Postgres exposed on host port 5442 via Docker.
- Cache: Redis exposed on host port 6380 via Docker.
- Prisma: `prisma generate` must be run after dependencies; rerun after schema changes.
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`
- AI: By default uses a local HF text-generation model. To use Google Gemini instead, set `GEMINI_API_KEY` and (optionally) `GEMINI_MODEL` in `.env`; the backend will switch to Gemini automatically.

## Useful commands
- Start services only: `docker compose up -d`
- Stop services: `docker compose down`
- View logs: `docker compose logs -f`
- Apply schema without migrations: `prisma db push`

Key URLs (default):
- API base: `http://localhost:8000`
- Products: `GET /api/products`
- AI chat: `POST /api/chat` with `{"message": "...", "context": "optional"}`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Environment
- `DATABASE_URL` should match the Postgres container; default points to localhost:5442.
- `REDIS_URL` defaults to `redis://localhost:6380/0`.
- AI model defaults to `distilgpt2`; set `MODEL_NAME` to another HF model id as needed.

## Prisma notes
- Schema: `prisma/schema.prisma`
- Run `prisma db push` for schema-only sync (no migrations) if you prefer.
- Regenerate client after schema changes: `prisma generate`.

## Caching
- Product list responses are cached in Redis for 60 seconds (`products:{category}` keys). Adjust in `app/services/product_service.py`.

## Health check
- `GET /health` returns `{ "status": "ok" }`.
