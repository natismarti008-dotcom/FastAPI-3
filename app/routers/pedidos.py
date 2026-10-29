from fastapi import APIRouter, HTTPException

from app.database import conectar
from app.schemas import PedidoCrear

router = APIRouter(
    prefix="/pedidos",
    tags=["Pedidos"]
)


# CREAR PEDIDO
@router.post("", status_code=201)
def crear(datos: PedidoCrear):

    with conectar() as db:
        with db.cursor() as cur:

            # Validar cliente
            cur.execute(
                """
                SELECT id_cliente
                FROM clientes
                WHERE id_cliente=%s
                """,
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
                    SELECT stock
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


# LISTAR PEDIDOS
@router.get("")
def listar():

    return {
        "mensaje": "Listado de pedidos"
    }


# DETALLE PEDIDO
@router.get("/{pedido_id}")
def detalle(pedido_id: int):

    return {
        "pedido_id": pedido_id
    }


# RETO B - CAMBIAR ESTADO
@router.patch("/{pedido_id}/estado")
def cambiar_estado(
    pedido_id: int,
    estado: str
):

    with conectar() as db:
        with db.cursor() as cur:

            cur.execute(
                """
                SELECT estado
                FROM pedidos
                WHERE id_pedido=%s
                """,
                (pedido_id,)
            )

            pedido = cur.fetchone()

            if pedido is None:
                raise HTTPException(
                    status_code=404,
                    detail="Pedido no encontrado"
                )

            estado_actual = pedido["estado"]

            if estado_actual != "pendiente":
                raise HTTPException(
                    status_code=409,
                    detail="Solo los pedidos pendientes pueden cambiar de estado"
                )

            if estado not in [
                "confirmado",
                "cancelado"
            ]:
                raise HTTPException(
                    status_code=400,
                    detail="Estado inválido"
                )

            cur.execute(
                """
                UPDATE pedidos
                SET estado=%s
                WHERE id_pedido=%s
                """,
                (
                    estado,
                    pedido_id
                )
            )

            return {
                "mensaje": "Estado actualizado",
                "nuevo_estado": estado
            }


# RETO D - CANCELAR PEDIDO
@router.post("/{pedido_id}/cancelar")
def cancelar_pedido(pedido_id: int):

    with conectar() as db:
        with db.cursor() as cur:

            # Buscar pedido
            cur.execute(
                """
                SELECT estado
                FROM pedidos
                WHERE id_pedido=%s
                """,
                (pedido_id,)
            )

            pedido = cur.fetchone()

            if pedido is None:
                raise HTTPException(
                    status_code=404,
                    detail="Pedido no encontrado"
                )

            # Evitar doble cancelación
            if pedido["estado"] == "cancelado":
                raise HTTPException(
                    status_code=409,
                    detail="El pedido ya fue cancelado"
                )

            # Obtener detalle del pedido
            cur.execute(
                """
                SELECT
                    producto_id,
                    cantidad
                FROM detalle_pedidos
                WHERE pedido_id=%s
                """,
                (pedido_id,)
            )

            detalles = cur.fetchall()

            # Devolver stock
            for item in detalles:

                cur.execute(
                    """
                    UPDATE productos
                    SET stock = stock + %s
                    WHERE id_producto=%s
                    """,
                    (
                        item["cantidad"],
                        item["producto_id"]
                    )
                )

            # Cambiar estado
            cur.execute(
                """
                UPDATE pedidos
                SET estado='cancelado'
                WHERE id_pedido=%s
                """,
                (pedido_id,)
            )

            return {
                "mensaje": "Pedido cancelado correctamente",
                "pedido_id": pedido_id,
                "estado": "cancelado"
            }