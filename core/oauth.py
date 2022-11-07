from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel

from core.config import settings

private_key = open('private_key.pem').read()
public_key = open('public_key.key').read()

class Setting(BaseModel):
    authjwt_secret_key: str = settings.SECRET_KEY
    authjwt_algorithm: str = 'RS256'
    authjwt_public_key: str = public_key
    authjwt_private_key: str = private_key

@AuthJWT.load_config
def get_config():
    return Setting()


