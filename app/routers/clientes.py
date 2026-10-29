from fastapi import APIRouter, HTTPException
from pymysql.err import IntegrityError

from app.database import conectar
from app.schemas import ClienteCrear, ClienteRespuesta

# Crea las rutas relacionadas con los clientes
router = APIRouter(
    prefix="/clientes",
    tags=["Clientes"]
)


# Obtener la lista de todos los clientes registrados
@router.get("", response_model=list[ClienteRespuesta])
def listar():
    with conectar() as db:
        with db.cursor() as cur:
            cur.execute(
                "SELECT id_cliente, nombre, email FROM clientes ORDER BY id_cliente"
            )
            return cur.fetchall()


# Buscar un cliente por su ID
@router.get("/{cliente_id}", response_model=ClienteRespuesta)
def obtener(cliente_id: int):
    with conectar() as db:
        with db.cursor() as cur:

            # Consulta el cliente según el ID recibido
            cur.execute(
                "SELECT id_cliente, nombre, email FROM clientes WHERE id_cliente=%s",
                (cliente_id,)
            )

            # Guarda el resultado de la búsqueda
            cliente = cur.fetchone()

            # Si el cliente no existe, muestra un error
            if cliente is None:
                raise HTTPException(
                    status_code=404,
                    detail="Cliente no encontrado"
                )

            # Devuelve la información del cliente encontrado
            return cliente


# Registrar un nuevo cliente en la base de datos
@router.post("", response_model=ClienteRespuesta, status_code=201)
def crear(datos: ClienteCrear):
    try:
        with conectar() as db:
            with db.cursor() as cur:

                # Inserta el nombre y correo del nuevo cliente
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

                # Obtiene el ID generado automáticamente
                nuevo_id = cur.lastrowid

                # Consulta el cliente recién creado
                cur.execute(
                    """
                    SELECT id_cliente, nombre, email
                    FROM clientes
                    WHERE id_cliente=%s
                    """,
                    (nuevo_id,)
                )

                # Devuelve los datos del cliente creado
                return cur.fetchone()

    except IntegrityError as exc:
        # Evita registrar correos repetidos
        raise HTTPException(
            status_code=409,
            detail="Correo ya registrado"
        ) from exc