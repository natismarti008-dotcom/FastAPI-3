from fastapi import APIRouter, HTTPException

from app.database import conectar
from app.schemas import PedidoCrear

router = APIRouter(
    prefix="/pedidos",
    tags=["Pedidos"]
)


@router.post("", status_code=201)
def crear(datos: PedidoCrear):

    with conectar() as db:
        with db.cursor() as cur:

            # Validar cliente
            cur.execute(
                "SELECT id_cliente FROM clientes WHERE id_cliente=%s",
                (datos.cliente_id,)
            )

            cliente = cur.fetchone()

            if cliente is None:
                raise HTTPException(
                    status_code=404,
                    detail="Cliente no encontrado"
                )

            # Validar productos y stock
            for item in datos.items:

                cur.execute(
                    """
                    SELECT id_producto, stock
                    FROM productos
                    WHERE id_producto=%s
                    """,
                    (item.producto_id,)
                )

                producto = cur.fetchone()

                if producto is None:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Producto {item.producto_id} no encontrado"
                    )

                if producto["stock"] < item.cantidad:
                    raise HTTPException(
                        status_code=409,
                        detail=f"Stock insuficiente del producto {item.producto_id}"
                    )

            return {
                "mensaje": "Pedido creado correctamente",
                "cliente_id": datos.cliente_id,
                "items": len(datos.items)
            }


@router.get("")
def listar():
    return {
        "mensaje": "Listado de pedidos"
    }


@router.get("/{pedido_id}")
def detalle(pedido_id: int):

    return {
        "pedido_id": pedido_id
    }