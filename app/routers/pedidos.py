from fastapi import APIRouter, HTTPException
from app.schemas import PedidoCrear

router = APIRouter(
    prefix="/pedidos",
    tags=["Pedidos"]
)

pedidos = []


@router.post("", status_code=201)
def crear(datos: PedidoCrear):

    nuevo_pedido = {
        "id": len(pedidos) + 1,
        "cliente_id": datos.cliente_id,
        "items": [item.dict() for item in datos.items]
    }

    pedidos.append(nuevo_pedido)

    return nuevo_pedido


@router.get("")
def listar():
    return pedidos


@router.get("/{pedido_id}")
def detalle(pedido_id: int):

    for pedido in pedidos:
        if pedido["id"] == pedido_id:
            return pedido

    raise HTTPException(
        status_code=404,
        detail="Pedido no encontrado"
    )