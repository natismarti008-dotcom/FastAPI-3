from decimal import Decimal
from pydantic import BaseModel, Field, EmailStr


# =========================
# CLIENTES
# =========================

# Modelo para registrar un nuevo cliente
class ClienteCrear(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    email: EmailStr


# Modelo para mostrar la información de un cliente
class ClienteRespuesta(BaseModel):
    id_cliente: int
    nombre: str
    email: EmailStr


# =========================
# PRODUCTOS
# =========================

# Modelo para crear un nuevo producto
class ProductoCrear(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)

    # Valida que el precio sea mayor que cero
    precio: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2
    )

    # Valida que el stock no sea negativo
    stock: int = Field(ge=0)


# Modelo para responder con los datos de un producto
class ProductoRespuesta(ProductoCrear):
    id_producto: int


# =========================
# PEDIDOS
# =========================

# Modelo para cada producto incluido en un pedido
class ItemPedido(BaseModel):

    # ID del producto solicitado
    producto_id: int = Field(gt=0)

    # Cantidad solicitada del producto
    cantidad: int = Field(gt=0)


# Modelo para crear un pedido
class PedidoCrear(BaseModel):

    # ID del cliente que realiza el pedido
    cliente_id: int = Field(gt=0)

    # Lista de productos incluidos en el pedido
    items: list[ItemPedido] = Field(min_length=1)