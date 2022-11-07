from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT

from sqlmodel import Session, select



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
	other_claims = { 'role': Authorize.get_raw_jwt()['role']}
	new_access_token = Authorize.create_access_token(subject=current_user, user_claims=other_claims)

	return { 'access_token': new_access_token }


@router.post('/login')
async def login(user: UserLogin, Authorize: AuthJWT = Depends()):
	print('fdsa', user)
	response = UserController.login(user)
	if not response.status :
		raise HTTPException(
			status_code=401, 
			detail="Incorrect username or password"
		)
	
	print(response)
	another_claims = { 'role': response.detail['role']  , 'data': response.detail }
	access_token = Authorize.create_access_token(subject=user.username, user_claims=another_claims)
	refresh_token = Authorize.create_refresh_token(subject=user.username, user_claims=another_claims)
	return { 'access_token': access_token, 'refresh_token': refresh_token, 'data': response.detail }



@router.post(
	'/verify/{token}'
)
async def verify_student_account(token: str, data: VerifyStudent, Authorize: AuthJWT = Depends()):
	Authorize.jwt_optional
	name = Authorize.get_jwt_subject() or 'anonymous'

	with Session(engine) as session:
		result  = session.exec(select(User).where(User.verify_token == token))
		user = result.first()


	if user == None:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Verify token not found"
		)
	if user.verified == True:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail="User already verified"
		)
	if UserController.username_exists(data.username):
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail="Username already exists"
		)
	
	student = StudentsController.update_to_verify(token, data)

	return student

	