from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT

from sqlmodel import Session, select



router = APIRouter() 


# ================= GET REQUESTS =================

@router.get(
    '',
)
async def get_all_departments(Authorize: AuthJWT = Depends()):
    pass


@router.get(
    '/heads',
)
async def get_all_department_heads(Authorize: AuthJWT = Depends()):
    pass


@router.get(
    '/{departmentId}/teachers',
)
async def get_all_teachers_in_department(departmentId: str, Authorize: AuthJWT = Depends()):
    pass


@router.get(
    '/{departmentId}/students',
)
async def get_all_students_in_department(departmentId: str, Authorize: AuthJWT = Depends()):
    pass


@router.get(
    '/{departmentId}/classes',
)
async def get_all_classes_in_department(departmentId: str, Authorize: AuthJWT = Depends()):
    pass


# ================= POST REQUESTS =================

@router.post(
    '/',
)
async def create_new_department(payload, Authorize: AuthJWT = Depends()):
    pass


# ================= PUT REQUESTS =================

@router.put(
    '/{departmentId}',
)
async def update_department(departmentId: str, payload, Authorize: AuthJWT = Depends()): 
    pass


# ================= PUT REQUESTS =================

@router.delete(
    '/{departmentId}',
)
async def remove_department(departmentId: str):
    pass