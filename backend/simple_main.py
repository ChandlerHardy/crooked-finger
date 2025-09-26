from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Crooked Finger Crochet Assistant API",
    description="AI-powered crochet pattern translation and diagram generation",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Crooked Finger Crochet Assistant API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/crooked-finger/health"
        },
        "status": "Running locally without GraphQL (dependencies not installed)"
    }

@app.get("/crooked-finger/health")
async def health():
    return {
        "status": "healthy",
        "service": "crooked-finger",
        "version": "1.0.0",
        "mode": "local-testing"
    }

@app.get("/test")
async def test():
    return {
        "message": "Backend is working!",
        "features": [
            "FastAPI server running",
            "CORS configured",
            "Health check available",
            "Ready for GraphQL integration"
        ]
    }