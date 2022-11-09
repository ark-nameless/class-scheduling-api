from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT

from sqlmodel import Session, select

from postgrest.exceptions import APIError

from db.db import db
from schemas.users import LoginUser
from core.authentication import Authenticator
from core.uuid_slug import ID



router = APIRouter() 

@router.get("/user")
async def user(Authorize: AuthJWT = Depends()):
	Authorize.jwt_required()

	current_user = Authorize.get_jwt_subject()
	other_claims = Authorize.get_raw_jwt()['role']
	return { 'user': current_user, 'extra': other_claims}


@router.post('/refresh')
async def refresh(Authorize: AuthJWT = Depends()):
	Authorize.jwt_refresh_token_required()

	current_user = Authorize.get_jwt_subject()
	other_claims = { 'role': Authorize.get_raw_jwt()['role'] }
	new_access_token = Authorize.create_access_token(subject=current_user, user_claims=other_claims)

	return { 'access_token': new_access_token }



@router.post('/login')
async def login(user: LoginUser, Authorize: AuthJWT = Depends()):
	try: 
		login_user = db.supabase.table('users').select('*').eq('username', user.username).limit(1).single().execute()
	except APIError as e: 
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Incorrect username or password"
		)
	
	will_login = Authenticator.verify_password(user.password, login_user.data['password'])

	if bool(login_user.data) and not will_login :
		raise HTTPException(
			status_code=401, 
			detail="Incorrect username or password"
		)
	data = login_user.data
	id = ID.uuid2slug(str(data['id']))

	another_claims = { 'role': data['role']  , 'id': id }
	access_token = Authorize.create_access_token(subject=user.username, user_claims=another_claims)
	refresh_token = Authorize.create_refresh_token(subject=user.username, user_claims=another_claims)

	return { 'access_token': access_token, 
			 'refresh_token': refresh_token, 
			 'data': {
				'id': id, 
				'username': user.username, 
				'role': data['role']
				} 
		   }

