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

from schemas.teachers import NewUnverifiedTeacher, VerifyTeacherAccount



router = APIRouter() 


# ================= GET REQUESTS =================

@router.get(
    '',
)
async def get_all_teachers(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    user_request = Authorize.get_jwt_subject() or "anonymous"

    data = []
    try:
        teachers = db.supabase.rpc('get_all_teachers', {}).execute()
        
        for entry in teachers.data: 
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
    '/none-department-head',
)
async def get_all_none_department_head_teachers(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    user_request = Authorize.get_jwt_subject() or "anonymous"

    data = []
    try:
        teachers = db.supabase.rpc('get_not_dept_head_teachers', {}).execute()
        
        for entry in teachers.data: 
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
    '/{teacherId}/subject-loads'
)
async def get_teachers_active_subject_loads(teacherId: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    teacherId = ID.slug2uuid(teacherId)

    data = []
    try: 
        schedules = db.supabase.table('active_schedules').select('*').eq('teacher_id', uuid.UUID(teacherId).hex).execute()

        for entry in schedules.data: 
            entry['id'] = ID.uuid2slug(str(entry['id']))
            entry['teacher_id'] = ID.uuid2slug(str(entry['teacher_id']))
            data.append(entry)

        response_schedules = db.supabase.table('response_schedules').select('*').eq('teacher_id', uuid.UUID(teacherId).hex).execute()
        for entry in response_schedules.data: 
            entry['id'] = ID.uuid2slug(str(entry['id']))
            entry['teacher_id'] = ID.uuid2slug(str(entry['teacher_id']))
            data.append(entry)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong, please report to admin the error."
        )

    return { "data": data }


@router.get(
    '/{id}',
)
async def get_teacher_profile(id: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    user_request = Authorize.get_jwt_subject() or "anonymous"

    data = {}
    try:
        id = ID.slug2uuid(id)
        student = db.supabase.rpc('get_teacher_profile', {'search_id': id}).execute()
        
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


@router.get(
    '/{id}/schedules'
)
async def get_teacher_schedule(id: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    user_request = Authorize.get_jwt_subject() or "anonymous"


    data = []
    try:
        id = ID.slug2uuid(id)
        teachers = db.supabase.table('active_schedules').select('*').eq('teacher_id', uuid.UUID(id).hex).execute()
        
        for schedule in teachers.data: 
            schedule['id'] = ID.uuid2slug(str(schedule['id']))
            schedule['teacher_id'] = ID.uuid2slug(str(schedule['teacher_id']))

            data.append(schedule)

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
    '/{id}/profile'
)
async def get_teacher_profile(id: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    data = {}
    try:
        id = ID.slug2uuid(id)
        profile = db.supabase.table('teachers').select('*').eq('user_id', uuid.UUID(id).hex).single().execute()

        data['profile'] = profile.data
        data['profile']['user_id'] = ID.uuid2slug(str(profile.data['user_id']))

        credentials = db.supabase.table('users').select('username, email').eq('id', uuid.UUID(id).hex).single().execute()

        data['credentials'] = credentials.data

            

    except APIError as e: 
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message
        )
    except Exception as e: 
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

    return { 'data': data, 'status': 200 }


@router.get(
    '/{id}/teaching-assignment'
)
async def get_teacher_teaching_assignment(id: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    data = []
    try:
        id = ID.slug2uuid(id)
        schedules = db.supabase.table('active_schedules').select('*').eq('teacher_id', uuid.UUID(id).hex).execute()

        for idx, load in enumerate(schedules.data): 
            if schedules.data != []:
                print(schedules.data)
                class_info = db.supabase.table('classes').select('name, students').contains('subject_loads', [schedules.data[idx]['id']]).execute()
                if class_info.data == []: continue

            days = ''
            times = ''
            for schedule in load['schedules']:
                days += ''.join(schedule['days']) + ' '
                times += f"{schedule['startTime'].split(' ')[0]}-{schedule['endTime'].split(' ')[0]} "

            # TODO: Fix class student when no students is enrolled.
            data.append({
                'section_id': load['section_id'],
                'subject_id': load['subject_id'],
                'description': load['description'],
                'units': load['units'],
                'hours': load['hours'],
                'college': class_info.data[0]['name'],
                'class_size': len(class_info.data[0]['students'] or []),
                'days': days,
                'time': times,
            })

    except APIError as e: 
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message
        )
    except Exception as e: 
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

    # print(data)
    
    return { 'data': data, 'status': 200 }



# ================= POST REQUESTS =================

@router.post(
    '',
)
async def register_unverified_teacher(payload: NewUnverifiedTeacher, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
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
        user = db.supabase.table('users').insert({'email': payload.email, 'token': secrets.token_urlsafe(), 'role': 'Teacher'}).execute()
        student = db.supabase.table('teachers').insert({'user_id': user.data[0]['id'], 'department_id': department_id}).execute()

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


# ================= PUT REQUESTS =================

@router.put(
    '/{tokenId}',
)
async def verify_teacher_information(tokenId: str, payload: VerifyTeacherAccount, Authorize: AuthJWT = Depends()): 
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
        teacher_update = {**payload.teacher.dict()}
        update_user = db.supabase.table('users').update(user_update).eq('token', tokenId).execute().data[0]
        update_teacher = db.supabase.table('teachers').update(teacher_update).eq('user_id', update_user['id']).execute()
    except: 
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong"
        )

    return { 'data': { 'detail': 'Account Verification Successful'}, 'status': 200 }


@router.put(
    '/{id}/update-credentials'
)
async def update_teacher_credentials(id: str, payload: dict, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    try:
        id = ID.slug2uuid(id)

        username = db.supabase.table('users').select('id, username').eq('username', payload['username']).execute().data
        user = db.supabase.table('users').select('username, email, password').eq('id', uuid.UUID(id).hex).single().execute()
        email_check = db.supabase.table('users').select('id, email').eq('email', payload['email']).execute()
        user = user.data

        
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

    if len(email_check.data) > 0 and ID.uuid2slug(str(email_check.data[0]['id']) != ID.uuid2slug(str(id))): 
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with the same email already exists"
        )
    if len(username) > 0 and ID.uuid2slug(str(username[0]['id']) != ID.uuid2slug(str(id))): 
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )
    if (not Authenticator.verify_password(payload['currentPassword'], user['password'])):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Unable to Update Information! Incorrect Password'
        )

    data = {
        'username': payload['username'],
        'email': payload['email'],
    }

    try:
        if payload['password'] is not None or payload['password'] == '':
            data['password'] = Authenticator.hash_password((payload['password']))

        user_update = db.supabase.table('users').update({**data}).eq('id', uuid.UUID(id).hex).execute()
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

    return { 'status': 200, 'detail': 'Successfully Updated!'}



@router.put(
    '/{id}/update-profile-info'
)
async def update_teacher_profile_info(id: str, payload: dict, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    try:
        id = ID.slug2uuid(id)

        user_profile = db.supabase.table('teachers').update({**payload}).eq('user_id', uuid.UUID(id).hex).execute()

        
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

    return { 'status': 200, 'detail': 'Successfully Updated!'}



# ================= PUT REQUESTS =================

