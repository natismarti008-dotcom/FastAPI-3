from fastapi import APIRouter, HTTPException, Query

from app.database import conectar
from app.schemas import ProductoCrear, ProductoRespuesta

# Define las rutas relacionadas con los productos
router = APIRouter(
    prefix="/productos",
    tags=["Productos"]
)


# Listar productos con búsqueda y paginación
@router.get("", response_model=list[ProductoRespuesta])
def listar(
    buscar: str | None = None,
    pagina: int = Query(1, ge=1),
    limite: int = Query(10, ge=1, le=50)
):
    # Consulta base para obtener productos
    sql = """
    SELECT id_producto, nombre, precio, stock
    FROM productos
    """

    # Lista para almacenar parámetros de la consulta
    params = []

    # Si se envía un nombre, filtra los productos
    if buscar:
        sql += " WHERE nombre LIKE %s"
        params.append(f"%{buscar}%")

    # Ordena los resultados y aplica paginación
    sql += " ORDER BY id_producto LIMIT %s OFFSET %s"

    params.extend([
        limite,
        (pagina - 1) * limite
    ])

    # Ejecuta la consulta y devuelve los resultados
    with conectar() as db:
        with db.cursor() as cur:
            cur.execute(sql, tuple(params))
            return cur.fetchall()


# Obtener un producto por su ID
@router.get("/{producto_id}", response_model=ProductoRespuesta)
def obtener(producto_id: int):

    with conectar() as db:
        with db.cursor() as cur:

            # Busca el producto según el ID recibido
            cur.execute(
                """
                SELECT id_producto, nombre, precio, stock
                FROM productos
                WHERE id_producto=%s
                """,
                (producto_id,)
            )

            # Guarda el resultado encontrado
            producto = cur.fetchone()

            # Si no existe el producto, muestra un error
            if producto is None:
                raise HTTPException(
                    status_code=404,
                    detail="Producto no encontrado"
                )

            # Devuelve la información del producto
            return producto


# Registrar un nuevo producto
@router.post("", response_model=ProductoRespuesta, status_code=201)
def crear(datos: ProductoCrear):

    with conectar() as db:
        with db.cursor() as cur:

            # Inserta el producto en la base de datos
            cur.execute(
                """
                INSERT INTO productos
                (nombre, precio, stock)
                VALUES (%s, %s, %s)
                """,
                (
                    datos.nombre,
                    datos.precio,
                    datos.stock
                )
            )

            # Obtiene el ID generado automáticamente
            nuevo_id = cur.lastrowid

            # Consulta el producto recién creado
            cur.execute(
                """
                SELECT id_producto, nombre, precio, stock
                FROM productos
                WHERE id_producto=%s
                """,
                (nuevo_id,)
            )

            # Devuelve la información del nuevo producto
            return cur.fetchone()


# Actualizar únicamente el stock de un producto
@router.patch("/{producto_id}/stock",
              response_model=ProductoRespuesta)
def cambiar_stock(
    producto_id: int,
    stock: int = Query(ge=0)
):

    with conectar() as db:
        with db.cursor() as cur:

            # Actualiza la cantidad disponible del producto
            cur.execute(
                """
                UPDATE productos
                SET stock=%s
                WHERE id_producto=%s
                """,
                (
                    stock,
                    producto_id
                )
            )

            # Verifica si el producto existe
            if cur.rowcount == 0:
                raise HTTPException(
                    status_code=404,
                    detail="Producto no encontrado"
                )

            # Consulta el producto actualizado
            cur.execute(
                """
                SELECT id_producto, nombre, precio, stock
                FROM productos
                WHERE id_producto=%s
                """,
                (producto_id,)
            )

            # Devuelve los datos actualizados
            return cur.fetchone()