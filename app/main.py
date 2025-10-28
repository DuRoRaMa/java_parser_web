from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import parse

app = FastAPI(
    title="Java Parser API",
    version="1.0.0",
    description="AST parser for Java source code"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(parse.router)

@app.get("/")
def root():
    return {
        "message": "Java Parser API",  # Упрощенное сообщение
        "version": "1.0.0",
        "endpoints": {
            "documentation": "/docs",
            "health": "/health",
            "parser": "/api/parse"
        }
    }

@app.get("/health")
def health():
    return {"status": "ok", "service": "java-parser"}