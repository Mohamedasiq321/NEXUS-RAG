from fastapi import FastAPI

app = FastAPI(
    title="NEXUS-RAG",
    description="Adaptive Enterprise Intelligence & Research Agent",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "project": "NEXUS-RAG",
        "status": "online",
        "version": "0.1.0",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }