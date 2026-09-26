from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.rag import router as rag_router
from app.api.documents import router as documents_router


app = FastAPI(
    title="NEXUS-RAG",
    description="Adaptive Enterprise Intelligence & Research Agent",
    version="0.1.0",
)

# Allow the React/Vite frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rag_router)
app.include_router(documents_router)


@app.get("/")
def root():
    return {
        "project": "NEXUS-RAG",
        "status": "online",
        "version": "0.1.0",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}