from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT

from sqlmodel import Session, select

from postgrest.exceptions import APIError

from db.db import db
from schemas.users import LoginUser
from core.authentication import Authenticator
from core.uuid_slug import ID
from core.mailer import Mailer



router = APIRouter() 

@router.get("/send-mail")
async def send_email(email: str):
    mailer = Mailer()

    mailer.send_password_reset(email, 'fdl;skajdsf')

    return { 'status': 'sent' }