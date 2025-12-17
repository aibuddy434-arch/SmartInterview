import warnings
import logging
import os

# Suppress specific deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pkg_resources")
warnings.filterwarnings("ignore", category=UserWarning, module="librosa")
warnings.filterwarnings("ignore", category=FutureWarning, module="librosa")
warnings.filterwarnings("ignore", category=UserWarning, module="coqui_tts")

# Set up logging to suppress specific warnings
logging.getLogger("librosa").setLevel(logging.ERROR)
logging.getLogger("pkg_resources").setLevel(logging.ERROR)
logging.getLogger("coqui_tts").setLevel(logging.ERROR)

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db import init_db, close_db
from app.config import settings
from routes import auth, candidates, admin, ai, interviews, public

app = FastAPI(
    title="AI Interview Avatar System",
    description="A full-stack system for conducting AI-powered interviews with customizable avatars",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(interviews.router, prefix="/api/interviews", tags=["Interviews"])
app.include_router(candidates.router, prefix="/api/candidates", tags=["Candidates"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI Services"])
app.include_router(public.router, prefix="/api/public", tags=["Public Access"])

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.on_event("shutdown")
async def shutdown_event():
    await close_db()

@app.get("/")
async def root():
    return {"message": "AI Interview Avatar System API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)

