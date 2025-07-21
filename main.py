from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import auth, companias, usuarios, pisos, clientes, register
from routers import match
from models import create_db_and_tables

app = FastAPI()

class CustomCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = "https://front-end-ygjn.vercel.app"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response

app.add_middleware(CustomCORSMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://front-end-ygjn.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

create_db_and_tables()

app.include_router(auth.router)
app.include_router(companias.router)
app.include_router(usuarios.router)
app.include_router(pisos.router)
app.include_router(clientes.router)
app.include_router(match.router)
app.include_router(register.router)

@app.get("/test-cors")
async def test_cors():
    return {"message": "CORS test endpoint"}
