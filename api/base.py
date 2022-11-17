from fastapi import APIRouter

from api.v1 import test

from api.v1 import departments
from api.v1 import auth
from api.v1 import students
from api.v1 import teachers 
from api.v1 import classes

api_router = APIRouter()

api_router.include_router(test.router, prefix='/test', tags=['Test Routes'])
api_router.include_router(auth.router, prefix='/auth', tags=['Authentication and Authorization'])
api_router.include_router(departments.router, prefix="/departments", tags=['Department'])
api_router.include_router(students.router,prefix='/students', tags=['Students'])
api_router.include_router(teachers.router, prefix='/teachers', tags=['Teachers'])
api_router.include_router(classes.router, prefix="/classes", tags=["Classes"])