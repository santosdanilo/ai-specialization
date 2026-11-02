# SEC Filings RAG Web

Next.js frontend for the [`sec-filings-rag-app`](../sec-filings-rag-app) backend
(FastAPI + hybrid retrieval + reranking over SEC filings).

## Code source

This project is based on and adapted from
[finlab-front](https://github.com/infoslack/finlab-front), which was itself built
as the frontend for this same RAG/agent backend.

Adaptations made for this repository:

- renamed package and branding (`finlab-frontend` → `sec-filings-web`);
- API proxy (`/api/rag`, `/api/agent`) destination driven by `BACKEND_URL`
  env var instead of hardcoded `http://localhost:8000`;
- response types tightened to the backend's `Literal` unions
  (`investment_grade`, `recommendation`, `time_horizon`, etc.);
- momentum/sentiment scores rendered as percentages (backend returns 0–1,
  the base project displayed them as `x/10`).

## How it works

The frontend proxies API calls through Next.js rewrites, avoiding CORS issues
during development:

| Frontend route | Backend endpoint (FastAPI) |
|---|---|
| `POST /api/rag` | `POST /rag` |
| `POST /api/agent` | `POST /agent` |

The UI is a single chat page with two modes:

- **RAG mode** — grounded answers with sources from filings;
- **Multi-Stream Analysis (agent)** — parallel fundamental, momentum, and
  sentiment analysis with a final BUY/HOLD/SELL recommendation.

## Running

1. Start the backend (from the monorepo root):

   ```sh
   uv run uvicorn sec_filings_rag.main:app --host 127.0.0.1 --port 8000
   ```

2. Configure the backend URL (optional, defaults to `http://localhost:8000`):

   ```sh
   cp .env.local.example .env.local
   ```

3. Start the frontend:

   ```sh
   npm install
   npm run dev
   ```

4. Open http://localhost:3000
