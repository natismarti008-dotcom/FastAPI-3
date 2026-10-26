from fastapi import APIRouter, HTTPException
from pymysql.err import IntegrityError

from app.database import conectar
from app.schemas import ClienteCrear, ClienteRespuesta

router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"]
)


@router.get("", response_model=list[ClienteRespuesta])
def listar():
    with conectar() as db:
        with db.cursor() as cur:
            cur.execute(
                "SELECT id_cliente, nombre, email FROM clientes ORDER BY id_cliente"
            )
            return cur.fetchall()


@router.get("/{cliente_id}", response_model=ClienteRespuesta)
def obtener(cliente_id: int):
    with conectar() as db:
        with db.cursor() as cur:

            cur.execute(
                "SELECT id_cliente, nombre, email FROM clientes WHERE id_cliente=%s",
                (cliente_id,)
            )

            cliente = cur.fetchone()

            if cliente is None:
                raise HTTPException(
                    status_code=404,
                    detail="Cliente no encontrado"
                )

            return cliente


@router.post("", response_model=ClienteRespuesta, status_code=201)
def crear(datos: ClienteCrear):
    try:
        with conectar() as db:
            with db.cursor() as cur:

                cur.execute(
                    """
                    INSERT INTO clientes (nombre, email)
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
                    SELECT id_cliente, nombre, email
                    FROM clientes
                    WHERE id_cliente=%s
                    """,
                    (nuevo_id,)
                )

                return cur.fetchone()

    except IntegrityError as exc:
        raise HTTPException(
            status_code=409,
            detail="Correo ya registrado"
        ) from exc