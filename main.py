# MatchingProps API - CORS Fixed Version
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import auth, companias, usuarios, pisos, clientes, register
from routers import match
from models import create_db_and_tables

app = FastAPI(
    title="MatchingProps API",
    description="Plataforma Inmobiliaria Inteligente",
    version="1.0.0"
)

# ✅ CORS Configuration - CORRECTED
# ❌ CANNOT use allow_origins=["*"] with allow_credentials=True
# ✅ MUST specify exact origins when using credentials
origins = [
    "https://front-end-ygjn.vercel.app",  # Your Vercel frontend
    "http://localhost:3000",              # Local development
    "http://localhost:8080",              # Alternative local port
    "http://127.0.0.1:3000",             # Local IP
    "http://127.0.0.1:8080"              # Alternative local IP
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,                # ✅ Specific origins instead of "*"
    allow_credentials=True,               # ✅ Now works with specific origins
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]                  # ✅ Better browser compatibility
)

# ❌ REMOVED CustomCORSMiddleware - it was conflicting with CORSMiddleware
# ✅ Standard CORSMiddleware is sufficient and more reliable

# Initialize database
create_db_and_tables()

# ✅ Health check endpoint for Render monitoring
@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "message": "MatchingProps API is running",
        "version": "1.0.0"
    }

# ✅ CORS test endpoint for debugging
@app.get("/test-cors")
async def test_cors():
    return {
        "message": "CORS test successful", 
        "status": "working",
        "origins": origins
    }

# Include all routers
app.include_router(auth.router)
app.include_router(companias.router)
app.include_router(usuarios.router)
app.include_router(pisos.router)
app.include_router(clientes.router)
app.include_router(match.router)
app.include_router(register.router)

# ✅ Root endpoint with API info
@app.get("/")
async def root():
    return {
        "message": "MatchingProps API", 
        "status": "running", 
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# ✅ Render-compatible port configuration
if __name__ == "__main__":
    import uvicorn
    # Use PORT environment variable (Render default: 10000)
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(
        app, 
        host="0.0.0.0",  # ✅ Required for Render
        port=port,       # ✅ Dynamic port from environment
        log_level="info"
    )
