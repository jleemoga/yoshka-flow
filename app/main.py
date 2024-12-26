from fastapi import FastAPI
from app.api.endpoints import validation

app = FastAPI(
    title="YoshkaFlow API",
    description="Backend API for YoshkaFlow - AI-driven entity research and metrics generation",
    version="0.1.0"
)

# Include routers
app.include_router(validation.router, prefix="/api")

@app.get("/")
async def root():
    """Root endpoint returning API status"""
    return {
        "status": "online",
        "message": "Welcome to YoshkaFlow API",
        "version": "0.1.0"
    }
