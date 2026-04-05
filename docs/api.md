# Gym Wear Backend API (FastAPI)

Base URL (local dev): `http://localhost:8000`

Swagger UI: `http://localhost:8000/docs`  
OpenAPI JSON: `http://localhost:8000/openapi.json`

## Health
- `GET /health` → `{ "status": "ok" }`

## Products
- `GET /products` (also available under `/api/products`)
  - Query params (optional):
    - `search` – text match on name/tags
    - `category` – exact category
    - `tag` – tag string
    - `size` – size substring match in `sizes`
  - Response 200: `Product[]`
  - Caching: 60s in Redis (keyed by filters).
  - Product shape:
    ```json
    {
      "id": "string",
      "name": "string",
      "price": 0,
      "category": "Tops|Bottoms|Sets|Outerwear|Footwear|…",
      "description": "string",
      "colors": ["string"],
      "tags": ["string"],
      "rating": 4.6,
      "image": "https://…",
      "stock": 10,
      "featured": true,
      "newArrival": false,
      "sizes": "XS,S,M,L,XL"
    }
    ```

## Recommendations
- `GET /recommendations` (also `/api/recommendations`)
  - Query params: `userId` (optional) — personalization hook
  - Response 200: `Product[]` (featured/new arrivals fallback)

## AI Chat
- `POST /chat` (also `/api/chat`)
  - Body:
    ```json
    { "message": "string", "history": [ { "role": "user|assistant", "content": "string" } ] }
    ```
  - Response 200: `{ "reply": "string" }`

### Notes for frontend integration
- `NEXT_PUBLIC_API_BASE` can point to `http://localhost:8000`; endpoints exist at both `/products` and `/api/products`.
- CORS is enabled; set allowed origins via `ALLOWED_ORIGINS='["https://yourdomain"]'` in `.env`.
- Errors return JSON `{ "error": "message" }` with appropriate status.
- Sample catalog seed: run `python scripts/seed.py` after `prisma migrate dev` to populate products for UI/dev testing.
