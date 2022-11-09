from fastapi import APIRouter

from api.v1 import departments
from api.v1 import auth


api_router = APIRouter()

api_router.include_router(auth.router, prefix='/auth', tags=['Authentication and Authorization'])
api_router.include_router(departments.router, prefix="/departments", tags=['Department'])