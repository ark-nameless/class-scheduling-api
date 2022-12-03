from datetime import datetime
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT

from postgrest.exceptions import APIError

from db.db import db
from core.uuid_slug import ID

from schemas.departments import CreateDepartment, UpdateDepartment



router = APIRouter() 


@router.get(
    '/{id}/class-info'
)
async def get_class_info(id: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    
    id = ID.slug2uuid(id)
    class_info = db.supabase.table('classes').select('*').eq('id', uuid.UUID(id).hex).execute()
    department_name = db.supabase.table('departments').select('name').eq('id', class_info.data[0]['department_id']).single().execute().data['name']
    data = {
        'id': ID.uuid2slug(str(class_info.data[0]['id'])),
        'name': class_info.data[0]['name'],
        'major': class_info.data[0]['major'],
        'semester': class_info.data[0]['semester'],
        'year': class_info.data[0]['year'],
        'department_name': department_name
    }

    return { **data }


@router.get(
    '/{id}/class-loads'
)
async def get_class_loads(id: str, Authorize: AuthJWT = Depends()):
    # Authorize.jwt_required()

    id = ID.slug2uuid(id)

    class_loads = db.supabase.rpc('get_class_loads', {'search_id': uuid.UUID(str(id)).hex }).execute()

    data = []
    for load in class_loads.data:
        load['id'] = ID.uuid2slug(str(load['id']))
        load['teacher_id'] = ID.uuid2slug(str(load['teacher_id']))
        data.append(load)

    return { 'data': data }


@router.get(
    '/{id}/class-students'
)
async def get_class_students(id: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    id = ID.slug2uuid(id)

    class_loads = db.supabase.rpc('get_class_students', {'search_id': uuid.UUID(str(id)).hex }).execute()
    data = []
    for student in class_loads.data: 
        student['id'] = ID.uuid2slug(str(student['id']))
        student['name'] = f"{student['name']['lastname'].capitalize()}, {student['name']['firstname'].capitalize()} {student['name']['middlename'].capitalize()[0]}"

    return { 'data': class_loads.data }


@router.get(
    '/{id}/students-not-in-class'
)
async def get_students_not_in_given_class_id(id: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    id = ID.slug2uuid(id)

    class_loads = db.supabase.rpc('get_students_not_in_class', {'search_id': uuid.UUID(str(id)).hex }).execute()
    data = []
    for student in class_loads.data: 
        student['id'] = ID.uuid2slug(str(student['id']))
        if (student['name'] == None): 
            student['name'] = ' '
        else:
            student['name'] = f"{student['name']['lastname'].capitalize()}, {student['name']['firstname'].capitalize()} {student['name']['middlename'].capitalize()[0]}"

    return { 'data': class_loads.data }




# ======================== POST ========================

@router.post(
    ''
)
async def create_new_class_schedule(payload: dict, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    class_info = { 
        'department_id': uuid.UUID(ID.slug2uuid(payload['department_id'])).hex,
        'major': payload['major'],
        'name': payload['name'],
        'semester': payload['semester'],
        'year': payload['year'],
        'subject_loads': []
    }

    

    # clean subject loads
    saved_loads = []
    for load in payload['subject_loads']: 
        try: 
            load['teacher_id'] = uuid.UUID(ID.slug2uuid(load['teacher_id'])).hex
            subject = db.supabase.table('active_schedules').insert(load).execute()
            saved_loads.append(subject.data[0]['id'])

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

    for load in payload['response_loads']:
        try: 
            load_id = uuid.UUID(ID.slug2uuid(load['id'])).hex
            removed = db.supabase.table('response_schedules').delete().eq('id', load_id).execute()
            load['teacher_id'] = uuid.UUID(ID.slug2uuid(load['teacher_id'])).hex
            del load['id']
            del load['teacher_name']
            subject = db.supabase.table('active_schedules').insert(load).execute()
            saved_loads.append(subject.data[0]['id'])

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

    class_info['subject_loads'] = saved_loads
    try:
        class_schedule = db.supabase.table('classes').insert(class_info).execute()
        pass
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

    print(payload)
    return { 'status': 200 }


@router.post(
    '/response-schedule'
)
async def create_new_response_schedule(payload: dict, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    id = payload['to_department']
    schedules = payload['schedules']

    id = uuid.UUID(ID.slug2uuid(id)).hex

    for load in schedules: 
        try: 
            load['teacher_id'] = ID.slug2uuid(str(load['teacher_id']))
            load['teacher_id'] = uuid.UUID(load['teacher_id']).hex
            schedule = {
                'department_id': id,
                **load
            }
            print(schedule)
            subject = db.supabase.table('response_schedules').insert(schedule).execute()

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
    
    return { 'status': 200, 'detail': "Successfully Saved!"}


@router.post(
    '/create-schedule-request'
)
async def create_new_schedule_request(payload: dict, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()


    try: 
        payload['from'] = uuid.UUID(ID.slug2uuid(str(payload['from']))).hex
        payload['to'] = uuid.UUID(ID.slug2uuid(str(payload['to']))).hex

        print(payload)
        subject = db.supabase.table('subject_requests').insert({ **payload }).execute()

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
    
    return { 'status': 200, 'detail': "Successfully Saved!"}




# ======================= PUT =======================


@router.put(
    '/{id}/add-students'
)
async def add_new_students_to_class(id: str, payload: dict, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    try:
        id = ID.slug2uuid(id)
        class_students = db.supabase.table('classes').select('students').eq('id', uuid.UUID(id).hex).execute()

        current_students_in_class = set()
        if class_students.data[0]['students'] is not None:
            current_students_in_class = set(class_students.data[0]['students'])

        add_students = set(map(lambda id: ID.slug2uuid(id), payload['students']))
        append_students = list(add_students.union(current_students_in_class))

        
        students = db.supabase.table('classes').update({'students': append_students}).eq('id', id).execute()

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
    length = len(payload['students'])

    return { 'detail': f"{length} students successfully added to the class." }


@router.put(
    '/{id}/class-info'
)
async def update_class_info(id: str, payload: dict, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    try:
        id = ID.slug2uuid(id)
        class_students = db.supabase.table('classes').update({**payload}).eq('id', uuid.UUID(id).hex).execute()

    except Exception as e: 
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

    return { 'detail': f"Class info updated!" }


@router.put(
    '/{id}/remove-students'
)
async def remove_student_from_class(id:str, payload: dict, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    try:
        id = ID.slug2uuid(id)
        class_students = db.supabase.table('classes').select('students').eq('id', uuid.UUID(id).hex).execute()

        remove_students = set(map(lambda id: ID.slug2uuid(id), payload['students']))
        class_students = set(class_students.data[0]['students'])
        updated_list = list(class_students.difference(remove_students))
        
        students = db.supabase.table('classes').update({'students': updated_list}).eq('id', id).execute()
    except Exception as e: 
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

    length = len(payload['students'])
    return {'detail': f"{length} students successfully removed."}


@router.put(
    '/{id}/update-subject-schedule'
)
async def update_subject_schedule(id: str, payload: dict, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    try: 
        id = ID.slug2uuid(id)

        payload['teacher_id'] = uuid.UUID(str(ID.slug2uuid(payload['teacher_id']))).hex

        updated = db.supabase.table('active_schedules').update({**payload}).eq('id', uuid.UUID(id).hex).execute()
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

    return { 'status': 200, 'detail': 'Updated class schedule.' }



@router.put(
    '/{id}/update-subject-info'
)
async def update_subject_info(id: str, payload: dict, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    try: 
        id = ID.slug2uuid(id)
        print(id)

        updated = db.supabase.table('active_schedules').update({**payload}).eq('id', uuid.UUID(id).hex).execute()
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

    return { 'status': 200, 'detail': 'Updated class schedule.' }


# ======================= DELETE =======================
@router.delete(
    '/{id}/archive'
)
async def archive_class(id: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    try:
        id = ID.slug2uuid(id)

        class_info = db.supabase.table('classes').select('*').eq('id', uuid.UUID(id).hex).single().execute()

        for load_id in class_info.data['subject_loads']:
            schedule = db.supabase.table('active_schedules').select('*').eq('id', load_id).single().execute()

            archive_load = db.supabase.table('archived_schedules').insert(schedule.data).execute()
            remove_load = db.supabase.table('active_schedules').delete().eq('id', load_id).execute()
        
        archive_class = db.supabase.table('archived_classes').insert(class_info.data).execute()
        remove_class = db.supabase.table('classes').delete().eq('id', uuid.UUID(id).hex).execute()


    except Exception as e: 
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

    return {'status': 200, 'detail': f"Successfully archived."}