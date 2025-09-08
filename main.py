# MatchingProps API - CORS Fixed Version
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import auth, companias, usuarios, pisos, clientes, register, asesores
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
# ✅ CORS Configuration - Multi-environment support


ENVIRONMENT = os.getenv("ENVIRONMENT", "production")

if ENVIRONMENT == "test":
    origins = [
        "https://front-end-test-git-develop-julians-projects-1b5ab696.vercel.app",  # ← URL CORRECTA
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080"
    ]
    print("🧪 Running in TEST environment")
else:
    # Producción (mantener URLs actuales)
    origins = [
        "https://matchingprops.com",                    # ← Tus URLs de producción actuales
        "https://www.matchingprops.com",
        "https://front-end-ygjn.vercel.app",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080"
    ]
    print("🚀 Running in PRODUCTION environment")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# ✅ Add error handling middleware
from fastapi.responses import JSONResponse  # AGREGAR ESTE IMPORT AL INICIO

@app.middleware("http")
async def catch_exceptions_middleware(request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        import logging
        logging.error(f"Unhandled exception: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Internal server error: {str(e)}"}
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
app.include_router(asesores.router)

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

# 🔍 Debug endpoint para verificar variables de entorno
@app.get("/debug/environment")
async def debug_environment():
    return {
        "environment": os.getenv("ENVIRONMENT", "not_set"),
        "allow_reset": os.getenv("ALLOW_DATABASE_RESET", "not_set"),
        "database_url_set": bool(os.getenv("DATABASE_URL")),
        "secret_key_set": bool(os.getenv("SECRET_KEY"))
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
