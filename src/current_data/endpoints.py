from typing import Any

from fastapi import APIRouter, Request

router = APIRouter()


@router.post("/powerflow")
async def powerflow(request: Request) -> Any:
    return {"status": "ok"}


@router.post("/meter")
async def meter(request: Request) -> Any:
    return {"status": "ok"}
