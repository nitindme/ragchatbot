from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
import asyncio
from contextlib import asynccontextmanager
from app.core.database import engine, Base
from app.core.rate_limit import limiter
from app.api import admin, chat, auth, feedback

# Create tables
Base.metadata.create_all(bind=engine)

# Background task for document processing
background_task = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start background processor on startup"""
    global background_task
    from app.services.background_processor import start_background_processor
    
    # Start background processor
    background_task = asyncio.create_task(start_background_processor())
    print("✅ Background document processor started")
    
    yield
    
    # Cleanup on shutdown
    if background_task:
        background_task.cancel()
        print("🛑 Background document processor stopped")

app = FastAPI(
    title="Delhi Police Chatbot API",
    description="RAG-powered chatbot with admin document management",
    version="1.0.0",
    lifespan=lifespan
)

# CORS - Must be added first
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include routers
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(chat.router)
app.include_router(feedback.router)

@app.get("/")
def root():
    return {
        "message": "RAG Chatbot API",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
