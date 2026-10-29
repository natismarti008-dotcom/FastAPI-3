from fastapi import APIRouter, HTTPException
from pymysql.err import IntegrityError

from app.database import conectar
from app.schemas import ClienteCrear, ClienteRespuesta

router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"]
)


# Listar todos los clientes
@router.get("", response_model=list[ClienteRespuesta])
def listar():

    with conectar() as db:
        with db.cursor() as cur:

            cur.execute(
                """
                SELECT
                    id_cliente,
                    nombre,
                    email
                FROM clientes
                ORDER BY id_cliente
                """
            )

            return cur.fetchall()


# Obtener cliente por ID
@router.get("/{cliente_id}", response_model=ClienteRespuesta)
def obtener(cliente_id: int):

    with conectar() as db:
        with db.cursor() as cur:

            cur.execute(
                """
                SELECT
                    id_cliente,
                    nombre,
                    email
                FROM clientes
                WHERE id_cliente=%s
                """,
                (cliente_id,)
            )

            cliente = cur.fetchone()

            if cliente is None:
                raise HTTPException(
                    status_code=404,
                    detail="Cliente no encontrado"
                )

            return cliente


# Crear cliente
@router.post("", response_model=ClienteRespuesta, status_code=201)
def crear(datos: ClienteCrear):

    try:

        with conectar() as db:
            with db.cursor() as cur:

                cur.execute(
                    """
                    INSERT INTO clientes
                    (nombre, email)
                    VALUES (%s, %s)
                    """,
                    (
                        datos.nombre,
                        str(datos.email)
                    )
                )

                nuevo_id = cur.lastrowid

                cur.execute(
                    """
                    SELECT
                        id_cliente,
                        nombre,
                        email
                    FROM clientes
                    WHERE id_cliente=%s
                    """,
                    (nuevo_id,)
                )

                return cur.fetchone()

    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Correo ya registrado"
        )


@router.get("/{cliente_id}/pedidos")
def pedidos_cliente(cliente_id: int):

    with conectar() as db:
        with db.cursor() as cur:

            cur.execute(
                """
                SELECT
                    p.id_pedido,
                    p.fecha
                FROM pedidos p
                WHERE p.id_cliente = %s
                ORDER BY p.fecha DESC
                """,
                (cliente_id,)
            )

            return cur.fetchall()