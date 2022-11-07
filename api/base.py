from fastapi import APIRouter

from api.v1 import departments


api_router = APIRouter()

api_router.include_router(departments.router, prefix="/departments", tags=['Department'])