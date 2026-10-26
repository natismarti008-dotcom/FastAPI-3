from fastapi import APIRouter

router = APIRouter(
    prefix="/pedidos",
    tags=["Pedidos"]
)

@router.get("/")
def listar_pedidos():
    return [{"id": 1, "cliente": 1}]

