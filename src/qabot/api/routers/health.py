from fastapi import APIRouter
from fastapi.responses import JSONResponse

health_router = APIRouter()
@health_router.get("/health")
async def health() -> JSONResponse:
    """Simple health check for readiness/liveness probes."""
    return JSONResponse(content={"status": "ok"}, status_code=200)