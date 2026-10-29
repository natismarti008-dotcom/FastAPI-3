from decimal import Decimal
from fastapi import APIRouter, HTTPException
from app.database import conectar
from app.schemas import PedidoCrear, PedidoEstadoActualizar

router = APIRouter(prefix='/pedidos', tags=['Pedidos'])



@router.post("/{id_pedido}/cancelar")
def cancelar(id_pedido: int):

    with conectar() as db:
        with db.cursor() as cur:

            # Buscar pedido
            cur.execute(
                """
                SELECT id_pedido, estado
                FROM pedidos
                WHERE id_pedido = %s
                FOR UPDATE
                """,
                (id_pedido,)
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

            # Obtener productos del pedido
            cur.execute(
                """
                SELECT
                    id_producto,
                    cantidad
                FROM detalles_pedidos
                WHERE id_pedido = %s
                """,
                (id_pedido,)
            )

            detalles = cur.fetchall()

            # Devolver stock
            for detalle in detalles:

                cur.execute(
                    """
                    UPDATE productos
                    SET stock = stock + %s
                    WHERE id_producto = %s
                    """,
                    (
                        detalle["cantidad"],
                        detalle["id_producto"]
                    )
                )

            # Actualizar estado
            cur.execute(
                """
                UPDATE pedidos
                SET estado = 'cancelado'
                WHERE id_pedido = %s
                """,
                (id_pedido,)
            )

            return {
                "mensaje": "Pedido cancelado y stock devuelto",
                "pedido_id": id_pedido,
                "estado": "cancelado"
            }