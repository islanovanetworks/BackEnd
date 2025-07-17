from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Sin importar desde routers
import auth, companias, usuarios, pisos, clientes
from models import create_db_and_tables

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

create_db_and_tables()

# Incluir routers directamente
app.include_router(auth.router)
app.include_router(companias.router)
app.include_router(usuarios.router)
app.include_router(pisos.router)
app.include_router(clientes.router)

from routers import match
app.include_router(match.router)

import register
app.include_router(register.router)


