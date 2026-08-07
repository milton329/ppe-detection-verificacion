from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Hola mundo - PPE Detection API"}


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
