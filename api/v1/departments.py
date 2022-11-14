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
    user_request = Authorize.get_jwt_subject() or 'anonymous'

    data = []
    try:
        departmentId = ID.slug2uuid(departmentId)
        department_teachers = db.supabase.rpc('get_department_teachers', {'search_id': uuid.UUID(departmentId).hex }).execute()

        for entry in department_teachers.data: 
            data.append({
                "id": ID.uuid2slug(entry["id"]),
                "username": entry["username"],
                "email": entry["email"],
                "role": entry["role"],
                "name": entry['name']
            })
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.hint or e.detail
        )

    return { 'data': data, 'when': datetime.utcnow(), 'request_by': user_request }


@router.get(
    '/{departmentId}/students',
)
async def get_all_students_in_department(departmentId: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    user_request = Authorize.get_jwt_subject() or 'anonymous'

    data = []
    try:
        departmentId = ID.slug2uuid(departmentId)
        department_students = db.supabase.rpc('get_department_students', {'search_id': uuid.UUID(departmentId).hex }).execute()

        for entry in department_students.data: 
            data.append({
                "id": ID.uuid2slug(entry["id"]),
                "username": entry["username"],
                "email": entry["email"],
                "role": entry["role"],
                "name": entry['name']
            })
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.hint or e.detail
        )

    return { 'data': data, 'when': datetime.utcnow(), 'request_by': user_request }


# TODO Implement Classes
@router.get(
    '/{departmentId}/classes',
)
async def get_all_classes_in_department(departmentId: str, Authorize: AuthJWT = Depends()):

    pass

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


# ================= PUT REQUESTS =================

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