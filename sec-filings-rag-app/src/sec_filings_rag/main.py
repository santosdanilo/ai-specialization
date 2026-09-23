from fastapi import FastAPI

from sec_filings_rag.api.routers import rag, search

app = FastAPI(title="SEC Filings RAG")


@app.get("/")
def read_root():
    return {"status": "ok"}


app.include_router(search.router)
app.include_router(rag.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
