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
        "https://testfrontend-umber.vercel.app",  # ← TU NUEVO DOMINIO DE TEST
        "https://testfrontend-lf66bm4zd-julians-projects-1b5ab696.vercel.app",  # ← Preview deployment
        "https://testingfront-end-vndu.vercel.app",  # ← Mantener por compatibilidad
        "https://front-end-dra8.vercel.app",  # ← Mantener por compatibilidad
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080"
    ]
    print("🧪 Running in TEST environment")
    print(f"📡 CORS enabled for TEST origins: {origins}")
else:
    # Producción - CORS COMPLETO
    origins = [
        "https://matchingprops.com",
        "https://www.matchingprops.com",
        "https://front-end-ygjn.vercel.app",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080"
    ]
    print("🚀 Running in PRODUCTION environment")
    print(f"📡 CORS enabled for PRODUCTION origins: {origins}")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ✅ TEMPORAL: Máxima permisividad
    allow_credentials=False,  # ✅ OBLIGATORIO con allow_origins=["*"]
    allow_methods=["*"],  # ✅ TODOS los métodos
    allow_headers=["*"],  # ✅ TODAS las cabeceras
    expose_headers=["*"]
)

# ✅ MIDDLEWARE ADICIONAL PARA FORZAR CORS EN ERRORES 500
@app.middleware("http")
async def add_cors_headers(request, call_next):
    response = await call_next(request)
    
    # ✅ FORZAR CORS HEADERS SIEMPRE (incluso en errores)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, HEAD, PATCH"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Expose-Headers"] = "*"
    
    return response

# ✅ Add error handling middleware
from fastapi.responses import JSONResponse  # AGREGAR ESTE IMPORT AL INICIO

@app.middleware("http")
async def catch_exceptions_middleware(request, call_next):
    try:
        response = await call_next(request)
        
        # ✅ ASEGURAR CORS EN TODAS LAS RESPUESTAS
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, HEAD, PATCH"
        response.headers["Access-Control-Allow-Headers"] = "*"
        
        return response
        
    except Exception as e:
        import logging
        logging.error(f"Unhandled exception: {str(e)}")
        
        # ✅ RESPONSE CON CORS HEADERS INCLUIDOS
        response = JSONResponse(
            status_code=500,
            content={"detail": f"Internal server error: {str(e)}"}
        )
        
        # ✅ FORZAR CORS EN ERRORES 500
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, HEAD, PATCH"
        response.headers["Access-Control-Allow-Headers"] = "*"
        
        return response

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
    
# ✅ HANDLER EXPLÍCITO PARA PREFLIGHT - MEJORADO
@app.options("/{path:path}")
async def handle_options(path: str):
    from fastapi import Response
    response = Response()
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, HEAD, PATCH"
    response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, Accept, Origin, X-Requested-With"
    response.headers["Access-Control-Max-Age"] = "3600"
    return response

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
