from datetime import datetime
import json
import uuid
import secrets 

from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi_jwt_auth import AuthJWT

from postgrest.exceptions import APIError

from db.db import db
from core.uuid_slug import ID
from core.authentication import Authenticator

from schemas.students import NewUnverifiedStudent, VerifyStudentAccount



router = APIRouter() 


# ================= GET REQUESTS =================

@router.get(
    '',
)
async def get_all_students(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    user_request = Authorize.get_jwt_subject() or "anonymous"

    data = []
    try:
        students = db.supabase.rpc('get_all_students', {}).execute()
        
        for entry in students.data: 
            data.append({
                "id": ID.uuid2slug(entry["id"]),
                "username": entry["username"] or '',
                "email": entry["email"] or '',
                "role": entry["role"],
                "verified": entry['verified'],
                "name": entry["name"],
                "department_id": ID.uuid2slug(entry["department_id"]),
                "profile_img": entry['profile_img']  or '',
                "address": entry['address']  or '',
                "department_name": entry['department_name'],
                "abbrev": entry['abbrev']
            })
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e
        )

    return { 'data': data, 'request_by': user_request, 'when': datetime.utcnow() }


@router.get(
    '/verified',
)
async def get_all_verified_students(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    user_request = Authorize.get_jwt_subject() or "anonymous"

    data = []
    try:
        students = db.supabase.rpc('get_students', {'is_verified': True}).execute()

        for entry in students.data: 
            data.append({
                "id": ID.uuid2slug(entry["id"]),
                "username": entry["username"],
                "email": entry["email"],
                "name": entry["name"],
                "department_id": ID.uuid2slug(entry["department_id"]),
                "role": entry["role"],
            })
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e
        )

    return { 'data': data, 'request_by': user_request, 'when': datetime.utcnow() }


@router.get(
    '/unverified',
)
async def get_all_unverified_students(Authorize: AuthJWT = Depends()):
    Authorize.jwt_optional()
    user_request = Authorize.get_jwt_subject() or "anonymous"

    data = []
    try:
        students = db.supabase.rpc('get_students', {'is_verified': False}).execute()

        for entry in students.data: 
            data.append({
                "id": ID.uuid2slug(entry["id"]),
                "username": entry["username"],
                "email": entry["email"],
                "name": entry["name"],
                "department_id": ID.uuid2slug(entry["department_id"]),
                "role": entry["role"],
            })
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e
        )

    return { 'data': data, 'request_by': user_request, 'when': datetime.utcnow() }


@router.get(
    '/{id}',
)
async def get_student_profile(id: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_optional()
    user_request = Authorize.get_jwt_subject() or "anonymous"

    data = {}
    try:
        id = ID.slug2uuid(id)
        student = db.supabase.rpc('get_student_profile', {'search_id': id}).execute()
        
        data = student.data[0]

        data['id'] = ID.uuid2slug(data['id'])
        data['department_id'] = ID.uuid2slug(data['department_id'])
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e
        )

    return { 'data': data, 'request_by': user_request, 'when': datetime.utcnow() }


# ================= POST REQUESTS =================

@router.post(
    '',
)
async def add_unverified_student(payload: NewUnverifiedStudent, Authorize: AuthJWT = Depends()):
    Authorize.jwt_optional()
    user_request = Authorize.get_jwt_subject() or "anonymous"

    email_exist = db.supabase.table('users').select('email').eq('email', payload.email).execute()
    if len(email_exist.data) > 0: 
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with the same email already exists"
        )

    data = {}
    try:
        department_id = ID.slug2uuid(payload.department_id)
        user = db.supabase.table('users').insert({'email': payload.email, 'token': secrets.token_urlsafe(), 'role': 'Student'}).execute()
        student = db.supabase.table('students').insert({'user_id': user.data[0]['id'], 'department_id': department_id}).execute()

        user_data = user.data[0]
        user_data['id'] = ID.uuid2slug(str(user_data['id']))

        student_data = student.data[0]
        student_data['department_id'] = department_id

        department = db.supabase.table('departments').select('*').eq('id', department_id).execute()
        department_data = {
            'department_name': department.data[0]['name'],
            'abbrev': department.data[0]['abbrev'],
        }

    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e
        )

    return { 'data': {**user_data, **student_data, **department_data}, 'request_by': user_request, 'when': datetime.utcnow() }


    pass

# ================= PUT REQUESTS =================

@router.put(
    '/{tokenId}',
)
async def verify_student_information(tokenId: str, payload: VerifyStudentAccount): 
    print(payload)
    username = db.supabase.table('users').select('username').eq('username', payload.user.username).execute().data
    if len(username) > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )

    try: 
        user_update = { 
            'username': payload.user.username,
            'password': Authenticator.hash_password(payload.user.password),
            'token': '',
            'verified': True,
            'updated_at': str(datetime.utcnow())
        }
        student_update = {**payload.student.dict()}
        update_user = db.supabase.table('users').update(user_update).eq('token', tokenId).execute().data[0]
        update_student = db.supabase.table('students').update(student_update).eq('user_id', update_user['id']).execute()
    except Exception as e : 
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e
        )

    return { 'data': { 'detail': 'Account Verification Successful'}, 'status': 200 }


# ================= PUT REQUESTS =================

