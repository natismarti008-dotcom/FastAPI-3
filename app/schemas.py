from decimal import Decimal
from pydantic import BaseModel, Field, EmailStr


# =========================
# CLIENTES
# =========================

class ClienteCrear(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    email: EmailStr


class ClienteRespuesta(BaseModel):
    id_cliente: int
    nombre: str
    email: EmailStr


# =========================
# PRODUCTOS
# =========================

class ProductoCrear(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    precio: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2
    )
    stock: int = Field(ge=0)


class ProductoRespuesta(ProductoCrear):
    id_producto: int


# =========================
# PEDIDOS
# =========================

class ItemPedido(BaseModel):
    producto_id: int = Field(gt=0)
    cantidad: int = Field(gt=0)


class PedidoCrear(BaseModel):
    cliente_id: int = Field(gt=0)
    items: list[ItemPedido] = Field(min_length=1)