from fastapi import FastAPI

from app.routers import clientes
from app.routers import productos
from app.routers import pedidos

app = FastAPI(title="Tienda ADSO")

app.include_router(clientes.router)
app.include_router(productos.router)
app.include_router(pedidos.router)

@app.get("/")
def inicio():
    return {"mensaje": "API Tienda ADSO"}