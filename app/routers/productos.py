from fastapi import APIRouter

router = APIRouter(
    prefix="/productos",
    tags=["Productos"]
)

@router.get("/")
def listar_productos():
    return [{"id": 1, "nombre": "Laptop"}]

@router.post("/")
def crear_producto():
    return {"mensaje": "Producto registrado"}
@router.patch("/{id}/stock")
def actualizar_stock(id: int, stock: int):
    return {
        "id": id,
        "nuevo_stock": stock
    }
