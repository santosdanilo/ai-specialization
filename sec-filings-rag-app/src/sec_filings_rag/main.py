from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sec_filings_rag.api.routers import agent, rag, search

app = FastAPI(title="SEC Filings RAG")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"status": "ok"}


app.include_router(search.router)
app.include_router(rag.router)
app.include_router(agent.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
