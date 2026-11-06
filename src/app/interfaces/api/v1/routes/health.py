from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.interfaces.api.v1.dependencies import ContainerDep

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live")
async def liveness() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
async def readiness(container: ContainerDep) -> JSONResponse:
    if await container.database_is_reachable():
        return JSONResponse({"status": "ok", "database": "up"})
    return JSONResponse({"status": "unavailable", "database": "down"}, status_code=503)
