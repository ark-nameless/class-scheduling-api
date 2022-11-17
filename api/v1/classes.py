from datetime import datetime
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT

from postgrest.exceptions import APIError

from db.db import db
from core.uuid_slug import ID

from schemas.departments import CreateDepartment, UpdateDepartment



router = APIRouter() 



@router.post(
    ''
)
async def create_new_class_schedule(payload: dict):
    class_info = { 
        'department_id': uuid.UUID(ID.slug2uuid(payload['department_id'])).hex,
        'major': payload['major'],
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
                detail=e.__str__
            )

    class_info['subject_loads'] = saved_loads
    try:
        class_schedule = db.supabase.table('classes').insert(class_info).execute()
    except APIError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message
        )
    except Exception as e: 
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.__str__
        )

    return { 'status': 200 }







{
    'department_id': 'IW3Ivx1EQRCNwFV1M36cUw', 
    'major': 'Odio quaerat amet n', 
    'semester': 33, 
    'year': {
        'start': 1986, 
        'end': 1970
    }, 
    'subject_loads': [
        {
            'section_id': 'Dicta esse et et ame', 
            'subject_id': 'Rerum ipsum repudian', 
            'description': 'Dylan Goff', 
            'units': 20, 
            'hours': 94, 
            'teacher_id': 'FRvy3YQvSnOuhDJlt8wdAA', 
            'schedules': [
                {
                    'days': ['M', 'W'], 
                    'startTime': '9:00 AM', 
                    'endTime': '10:00 AM', 
                    'location': ''
                }
            ]
        }, {
            'section_id': 'Lorem eveniet est u', 
            'subject_id': 'Iste minima quia vel', 
            'description': 'Kelly Pitts', 
            'units': 22, 
            'hours': 15, 
            'teacher_id': 'KoPVn-8gRFWcRHVHTXdoyA', 
            'schedules': [
                {
                    'days': ['M', 'W'], 
                    'startTime': '9:00 AM', 
                    'endTime': '10:00 AM', 
                    'location': ''
                }
            ]
        }
    ]
}