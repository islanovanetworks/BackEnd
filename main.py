from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import auth, companias, usuarios, pisos, clientes, register
from routers import match
from models import create_db_and_tables

app = FastAPI()

origins = ["https://front-end-ygjn.vercel.app/"]  # Update to your Vercel domain, e.g., ["https://your-app.vercel.app"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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
