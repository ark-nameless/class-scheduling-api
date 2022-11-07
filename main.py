import uvicorn
from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi_jwt_auth.exceptions import AuthJWTException
from core.config import settings

from api import base


app = FastAPI()

app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)

origins = [
    '*',
    # "http://localhost",
    # "http://localhost:8000",
    # "http://loclahost:4200",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message
    }
)

app.include_router(base.api_router)