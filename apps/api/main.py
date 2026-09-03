from fastapi import FastAPI

app = FastAPI(title="rag-agent API")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
