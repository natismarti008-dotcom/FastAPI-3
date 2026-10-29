from fastapi import APIRouter, HTTPException
from pymysql.err import IntegrityError

from app.database import conectar
from app.schemas import ClienteCrear, ClienteRespuesta

router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"]
)


# LISTAR CLIENTES
@router.get("", response_model=list[ClienteRespuesta])
def listar():

    with conectar() as db:
        with db.cursor() as cur:

            cur.execute("""
                SELECT
                    id_cliente,
                    nombre,
                    email
                FROM clientes
                ORDER BY id_cliente
            """)

            return cur.fetchall()


# OBTENER CLIENTE POR ID
@router.get("/{cliente_id}", response_model=ClienteRespuesta)
def obtener(cliente_id: int):

    with conectar() as db:
        with db.cursor() as cur:

            cur.execute("""
                SELECT
                    id_cliente,
                    nombre,
                    email
                FROM clientes
                WHERE id_cliente=%s
            """, (cliente_id,))

            cliente = cur.fetchone()

            if cliente is None:
                raise HTTPException(
                    status_code=404,
                    detail="Cliente no encontrado"
                )

            return cliente


# CREAR CLIENTE
@router.post("", response_model=ClienteRespuesta, status_code=201)
def crear(datos: ClienteCrear):

    try:

        with conectar() as db:
            with db.cursor() as cur:

                cur.execute("""
                    INSERT INTO clientes
                    (nombre, email)
                    VALUES (%s, %s)
                """,
                (
                    datos.nombre,
                    str(datos.email)
                ))

                nuevo_id = cur.lastrowid

                cur.execute("""
                    SELECT
                        id_cliente,
                        nombre,
                        email
                    FROM clientes
                    WHERE id_cliente=%s
                """, (nuevo_id,))

                return cur.fetchone()

    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Correo ya registrado"
        )


# ACTUALIZAR CLIENTE (RETO C)
@router.put("/{cliente_id}", response_model=ClienteRespuesta)
def actualizar(cliente_id: int, datos: ClienteCrear):

    with conectar() as db:
        with db.cursor() as cur:

            cur.execute("""
                UPDATE clientes
                SET nombre=%s,
                    email=%s
                WHERE id_cliente=%s
            """,
            (
                datos.nombre,
                str(datos.email),
                cliente_id
            ))

            if cur.rowcount == 0:
                raise HTTPException(
                    status_code=404,
                    detail="Cliente no encontrado"
                )

            cur.execute("""
                SELECT
                    id_cliente,
                    nombre,
                    email
                FROM clientes
                WHERE id_cliente=%s
            """, (cliente_id,))

            return cur.fetchone()


# ELIMINAR CLIENTE (RETO C)
@router.delete("/{cliente_id}")
def eliminar(cliente_id: int):

    with conectar() as db:
        with db.cursor() as cur:

            cur.execute("""
                SELECT COUNT(*) AS cantidad
                FROM pedidos
                WHERE id_cliente=%s
            """, (cliente_id,))

            resultado = cur.fetchone()

            if resultado["cantidad"] > 0:
                raise HTTPException(
                    status_code=409,
                    detail="No se puede eliminar el cliente porque tiene pedidos"
                )

            cur.execute("""
                DELETE FROM clientes
                WHERE id_cliente=%s
            """, (cliente_id,))

            if cur.rowcount == 0:
                raise HTTPException(
                    status_code=404,
                    detail="Cliente no encontrado"
                )

            return {
                "mensaje": "Cliente eliminado correctamente"
            }


# RETO A
@router.get("/{cliente_id}/pedidos")
def pedidos_cliente(cliente_id: int):

    with conectar() as db:
        with db.cursor() as cur:

            cur.execute("""
                SELECT
                    p.id_pedido,
                    p.fecha
                FROM pedidos p
                WHERE p.id_cliente=%s
                ORDER BY p.fecha DESC
            """, (cliente_id,))

            return cur.fetchall()
    