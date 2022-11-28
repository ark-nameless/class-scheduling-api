import uuid
import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT


from postgrest.exceptions import APIError

from db.db import db
from schemas.users import LoginUser, AuthVerification, ForgotPassword
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
		if login_user.data['active'] == False:
			raise HTTPException(
				status_code=status.HTTP_403_FORBIDDEN,
				detail="Unfortunately your account has been suspended, please contact system admin for more information."
			)
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
	if len(id.data) < 1:
		id = db.supabase.table('students').select('departments:department_id(id)').eq('user_id', uuid.UUID(userId).hex).execute()
	
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
		user = db.supabase.table('users').select('token', 'email', 'verified').eq('id', uuid.UUID(id).hex).execute()

	except: 
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Invalid user id"
		)

	if user.data[0]['verified']: 
		raise HTTPException(
			status_code=status.HTTP_409_CONFLICT,
			detail="User is already verified"
		)
	elif len(user.data) < 1: 
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="User id not found"
		)

	data = user.data[0]

	mailer = Mailer()

	mailer.send_account_verification(data['email'], data['token'])

	return { 'status': 200, 'detail': 'Email verification successfully sent.' }



@router.post('/email/send-reset-password')
async def send_forgot_password_link_to_email_via_admin(payload: AuthVerification): 
	id = ID.slug2uuid(payload.id)
	try: 
		user = db.supabase.table('users').select('token', 'verified').eq('id', uuid.UUID(id).hex).execute()
		user_token = user.data[0]['token']
		
	except: 
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Invalid user id"
		)
	if user.data[0]['verified'] == False: 
		raise HTTPException(
			status_code=status.HTTP_409_CONFLICT,
			detail="User not verified yet. Please verify account first."
		)
	elif len(user.data) < 1: 
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="User id not found"
		)


	reset_user = db.supabase.table('users').update({'token': secrets.token_urlsafe()}).eq('id', id).execute()

	data = reset_user.data[0]
	mailer = Mailer()

	mailer.send_password_reset(data['email'], data['token'])

	return { 'status': 200, 'detail': 'Password reset email successfully sent.' }


@router.put('/email/reset-password')
async def send_forgot_password_link_to_email_using_email(payload: dict): 
	email = payload['email']
	try: 
		user = db.supabase.table('users').select('token', 'verified').eq('email', email).execute()

		user = user.data[0]
	except: 
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Invalid email id"
		)
	if user['verified'] == False: 
		raise HTTPException(
			status_code=status.HTTP_409_CONFLICT,
			detail="User not verified yet. Please verify account first."
		)
	if len(user) < 1: 
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="User email not found"
		)


	reset_user = db.supabase.table('users').update({'token': secrets.token_urlsafe()}).eq('email', email).execute()

	data = reset_user.data[0]
	mailer = Mailer()

	mailer.send_password_reset(email, data['token'])

	return { 'status': 200, 'detail': 'Password reset email successfully sent.' }



# =================== PUT =======================

@router.put(
	'/{token}/change-password'
)
async def change_user_password(token: str, payload: dict): 
	try: 
		user = db.supabase.table('users').select('*').eq('token', token).execute()
		print(payload)

		user = user.data[0]
		
	except: 
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST,
			detail="Invalid token"
		)
	if user['verified'] == False: 
		raise HTTPException(
			status_code=status.HTTP_409_CONFLICT,
			detail="User not verified yet. Please verify account first."
		)
	elif len(user) < 1: 
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Token not found"
		)

	payload = {
		'password': Authenticator.hash_password(payload['password']),
		'token': '',
	}


	reset_user = db.supabase.table('users').update(payload).eq('id', uuid.UUID(user['id']).hex).execute()

	return { 'status': 200, 'detail': 'Password changed successfully.' }

