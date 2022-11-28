from datetime import datetime
import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT

from postgrest.exceptions import APIError

from db.db import db
from core.uuid_slug import ID

from schemas.departments import CreateDepartment, UpdateDepartment



router = APIRouter() 


# ================= GET REQUESTS =================

@router.get(
    '',
)
async def get_all_departments(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    user_request = Authorize.get_jwt_subject() or "anonymous"

    departments = db.supabase.table('departments').select('*').execute()
    data = []

    for entry in departments.data:
        data.append({
            "id": ID.uuid2slug(entry['id']),
            "name": entry['name'],
            "abbrev": entry["abbrev"],
            "section_id": entry["section_id"],
            "head_id": ID.uuid2slug(entry['head_id']),
            "created_at": entry['created_at'],
            "updated_at": entry['updated_at']
        })

    return { 'data': data, 'when': datetime.utcnow(), 'request_by': user_request }


@router.get(
    '/heads',
)
async def get_all_department_heads(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    user_request = Authorize.get_jwt_subject() or "anonymous"

    department_heads = db.supabase.rpc('get_department_heads', {}).execute()
    data = []
    for head in department_heads.data: 
        data.append({
            'id': ID.uuid2slug(head['id']),
            'username': head['username'],
            'email': head['email'],
            'role': head['role'],
            'name': head['name'],
            'department_name': head['department_name'],
            'abbrev': head['abbrev'],
            'section_id': head['section_id']
        })


    return { 'data': data, 'when': datetime.utcnow(), 'request_by': user_request }


@router.get(
    '/{departmentId}/teachers',
)
async def get_all_teachers_in_department(departmentId: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    user_request = Authorize.get_jwt_subject() or "anonymous"

    data = []
    try:
        departmentId = ID.slug2uuid(departmentId)
        teachers = db.supabase.rpc('get_department_teachers', { 'search_id': uuid.UUID(departmentId).hex }).execute()
        print(departmentId)
        
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
    '/{departmentId}/students',
)
async def get_all_students_in_department(departmentId: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    user_request = Authorize.get_jwt_subject() or "anonymous"

    data = []
    try:
        departmentId = ID.slug2uuid(departmentId)
        students = db.supabase.rpc('get_department_students', {'search_id': uuid.UUID(departmentId).hex }).execute()
        
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
             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
             detail=e.hint or e.detail
        )

    return { 'data': data, 'request_by': user_request, 'when': datetime.utcnow() }


@router.get(
    '/{departmentId}/classes',
)
async def get_all_classes_in_department(departmentId: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    user_request = Authorize.get_jwt_subject() or "anonymous"

    departmentId = ID.slug2uuid(departmentId)
    classes = db.supabase.table('classes').select('*').eq('department_id', uuid.UUID(departmentId).hex).execute()


    data = []

    for entry in classes.data:
        data.append({
            "id": ID.uuid2slug(str(entry['id'])),
            "department_id": ID.uuid2slug(str(entry['department_id'])),
            "major": entry['major'],
            "semester": entry['semester'],
            "year": entry['year'],
            "subject_loads": list(map(lambda load: ID.uuid2slug(str(load)),entry['subject_loads'])),
            "students": entry['students'],
            "name": entry['name']
        })

    return { 'data': data, 'when': datetime.utcnow(), 'request_by': user_request }



@router.get(
    '/{departmentId}/subject-requests',
)
async def get_all_subject_requests_in_department(departmentId: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    user_request = Authorize.get_jwt_subject() or "anonymous"

    departmentId = ID.slug2uuid(departmentId)
    classes = db.supabase.table('subject_requests').select('*').eq('to', uuid.UUID(departmentId).hex).execute()


    data = []

    try: 
        for entry in classes.data:
            department_name = db.supabase.table('departments').select('name').eq('id', uuid.UUID(entry['from'])).execute()
            data.append({
                "id": ID.uuid2slug(str(entry['id'])),
                "from_id": ID.uuid2slug(str(entry['from'])),
                "from": department_name.data[0]['name'],
                "to": ID.uuid2slug(str(entry['to'])),
                "description": entry['description'],
                "subjects": entry['subjects'],
            })


    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= e.message
        )
    except Exception as e: 
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

    return { 'data': data, 'when': datetime.utcnow(), 'request_by': user_request }


@router.get(
    '/{departmentId}/subject-requests-responses',
)
async def get_all_subject_requests_reponses_in_department(departmentId: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    user_request = Authorize.get_jwt_subject() or "anonymous"

    departmentId = ID.slug2uuid(departmentId)
    classes = db.supabase.table('response_schedules').select('*').eq('department_id', uuid.UUID(departmentId).hex).execute()


    data = []

    try: 
        for entry in classes.data:
            teacher = db.supabase.table('teachers').select('*').eq('user_id', uuid.UUID(entry['teacher_id']).hex).execute()
            name = teacher.data[0]['name']
            name = f"{name['lastname']}, {name['firstname']} {name['middlename'][0]}"
            data.append({
                "id": ID.uuid2slug(str(entry['id'])),
                "teacher_id": ID.uuid2slug(str(entry['teacher_id'])),
                "section_id": entry['section_id'],
                "subject_id": entry['subject_id'],
                "description": entry['description'],
                "units": entry['units'],
                "hours": entry['hours'],
                "schedules": entry['schedules'],
                'teacher_name': name
            })


    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= e.message
        )
    except Exception as e: 
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

    return { 'data': data, 'when': datetime.utcnow(), 'request_by': user_request }
    





# ================= POST REQUESTS =================

@router.post(
    '',
)
async def create_new_department(payload: CreateDepartment, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    user_request = Authorize.get_jwt_subject() or "anonymous"
    try: 
        dept_abbrev = db.supabase.table('departments').select('abbrev').eq('abbrev', payload.abbrev).execute()
        if dept_abbrev.data: 
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Department abbreviation already exists"
            )
        
        section_id = db.supabase.table('departments').select('section_id').eq('section_id', payload.section_id).execute()
        if section_id.data:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Department section id already exists."
            )

        payload.head_id = ID.slug2uuid(payload.head_id)
        new_department = db.supabase.table('departments').insert({ **payload.dict() }).execute()
        if payload.head_id != None:
            print('change user info')
            update_user_department = db.supabase.table('teachers').update({'department_id': new_department.data[0]['id']}).eq('user_id', payload.head_id).execute()
            update_user_role = db.supabase.table('users').update({'role': 'Department Head'}).eq('id', payload.head_id).execute()

        new_department.data[0]['id'] = ID.uuid2slug(str(new_department.data[0]['id']))
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail= e.message
        )

    return { **new_department.data[0], 'when': datetime.utcnow(), 'request_by': user_request }

# ================= PUT REQUESTS =================

@router.put(
    '/{departmentId}',
)
async def update_department(departmentId: str, payload: UpdateDepartment, Authorize: AuthJWT = Depends()): 
    Authorize.jwt_required()
    user_request = Authorize.get_jwt_subject() or "anonymous"

    try: 
        if payload.abbrev != None:
            dept_abbrev = db.supabase.table('departments').select('abbrev').eq('abbrev', payload.abbrev).execute()
            if dept_abbrev.data: 
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Department abbreviation already exists"
                )
        if payload.section_id != None:
            section_id = db.supabase.table('departments').select('section_id').eq('section_id', payload.section_id).execute()
            if section_id.data:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Department section id already exists."
                )

        departmentId = ID.slug2uuid(departmentId)
        department = db.supabase.table('departments').update({ **payload.dict() }).eq('id', uuid.UUID(departmentId).hex).execute()
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail= e.message
        )

    return { **department.dict(), 'when': datetime.utcnow(), 'request_by': user_request }


# ================= DELETE REQUESTS =================

@router.delete(
    '/{departmentId}',
)
async def remove_department(departmentId: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    user_request = Authorize.get_jwt_subject() or "anonymous"

    try: 
        departmentId = ID.slug2uuid(departmentId)
        department = db.supabase.table('departments').delete().eq('id', uuid.UUID(departmentId).hex).execute()
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail= e.message
        )

    return { **department.dict(), 'when': datetime.utcnow(), 'request_by': user_request }

@router.delete(
    '/{requestId}/finish-request',
)
async def remove_department(requestId: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    try: 
        requestId = ID.slug2uuid(requestId)
        request = db.supabase.table('subject_requests').delete().eq('id', uuid.UUID(requestId).hex).execute()

    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail= e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail= str(e)
        )

    return { 'status': 200, 'detail': 'Successfully Finished!'}