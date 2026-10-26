
from fastapi import APIRouter, HTTPException

router = APIRouter(
    prefix="/pedidos",
    tags=["Pedidos"]
)

@router.post("/")
def crear_pedido(datos: dict):

    cliente_id = datos["cliente_id"]
    items = datos["items"]

    total = 0

    for item in items:

        producto_id = item["producto_id"]
        cantidad = item["cantidad"]

      
        precio = 35000

        subtotal = precio * cantidad
        total += subtotal

    return {
        "mensaje": "Pedido creado",
        "cliente_id": cliente_id,
        "total": total
    }
