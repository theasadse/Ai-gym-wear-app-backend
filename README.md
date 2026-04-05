# Gym Wear Backend (FastAPI + Prisma + Postgres + Redis)

Backend services for the gym-wear web application. Frontend lives separately. This repo wires FastAPI, PostgreSQL (via Prisma ORM), Redis caching, and a simple AI chat endpoint.

## Quick start (Dockerized Postgres + Redis)
```bash
cp .env.example .env
docker compose up -d  # starts Postgres and Redis

# in a virtualenv
pip install -r requirements.txt
prisma generate          # builds the Prisma Python client
prisma migrate dev --name init  # creates schema in Postgres (interactive)

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Key URLs (default):
- API base: `http://localhost:8000`
- Products: `GET /api/products`
- AI chat: `POST /api/chat` with `{"message": "...", "context": "optional"}`

## Environment
- `DATABASE_URL` should match the Postgres container; default points to localhost:5432.
- `REDIS_URL` defaults to `redis://localhost:6379/0`.
- AI model defaults to `distilgpt2`; set `MODEL_NAME` to another HF model id as needed.

## Prisma notes
- Schema: `prisma/schema.prisma`
- Run `prisma db push` for schema-only sync (no migrations) if you prefer.
- Regenerate client after schema changes: `prisma generate`.

## Caching
- Product list responses are cached in Redis for 60 seconds (`products:{category}` keys). Adjust in `app/services/product_service.py`.

## Health check
- `GET /health` returns `{ "status": "ok" }`.
