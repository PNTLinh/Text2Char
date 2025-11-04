from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Text2Chart API",
    description="Convert natural language to SQL and charts",
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

# Include routes
app.include_router(router, prefix="/api", tags=["query"])

@app.get("/")
async def root():
    return {
        "message": "Text2Chart API",
        "docs": "/docs",
        "health": "ok"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)