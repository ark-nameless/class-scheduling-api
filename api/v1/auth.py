import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT


from postgrest.exceptions import APIError

from db.db import db
from schemas.users import LoginUser, AuthVerification
from core.authentication import Authenticator
from core.uuid_slug import ID

from core.mailer import Mailer



router = APIRouter() 

@router.get('/')
def home():
	return { 'Hello': 'World' }

@router.get('/heath')
def heath_check():
	return {status.HTTP_200_OK}

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


@router.get('/verify-token/{tokenId}')
async def check_verify_account_token(tokenId: str, Authorize: AuthJWT = Depends()):
	try: 
		token = db.supabase.table('users').select('token').eq('token', tokenId).execute()
		print(len(token.data))
		if not bool(token.data):
			raise HTTPException(
				status_code=status.HTTP_404_NOT_FOUND,
				detail="Verification token does not exists"
			)
	except APIError as e: 
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Verification token does not exists"
		)

	return { 'status': True }


@router.get('/{userId}/department')
async def get_department_of_user(userId: str):
	print(userId)
	userId = ID.slug2uuid(userId)
	id = db.supabase.table('teachers').select('departments:department_id(id)').eq('user_id', uuid.UUID(userId).hex).execute()
	
	return { 'data': ID.uuid2slug(str(id.data[0]['departments']['id'])) }


@router.post('/email/reset-password')
async def send_email_for_password_reset(payload): 
	mailer = Mailer()

	mailer.send_password_reset(payload.email, payload.token)
	return { 'status': 200 }



@router.post('/email/verify-account')
async def send_email_for_verify_account(payload: AuthVerification): 
	id = ID.slug2uuid(payload.id)
	try: 
		user = db.supabase.table('users').select('token', 'email').eq('id', uuid.UUID(id).hex).execute()
	except: 
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Invalid user id"
		)
	if len(user.data) < 1: 
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="User id not found"
		)

	data = user.data[0]

	mailer = Mailer()

	mailer.send_account_verification(data['email'], data['token'])

	return { 'status': 200, 'detail': 'Email verification successfully sent.' }
