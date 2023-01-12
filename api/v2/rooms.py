import re
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT

from postgrest.exceptions import APIError

from db.db import db
from schemas.users import LoginUser
from core.authentication import Authenticator
from core.uuid_slug import ID
from core.mailer import Mailer



router = APIRouter() 


@router.get("/")
async def get_all_used_room(Authorize = Depends(AuthJWT)):
    data = db.supabase.table('active_schedules').select('schedules').execute()

    return {'data': data}


@router.get("/schedules/{room_name}")
async def get_room_schedules(room_name: str, Authorize = Depends(AuthJWT)):

    def get_time_val(time):
        start_time = re.sub("[^0-9]", "", time['startTime'])
        val = int(start_time) if time['startTime'].find('AM') != -1 else int(start_time) + 1200 if int(start_time) == 1200 else 1200
        return val


    room_name = room_name.strip()

    data = db.supabase.table('active_schedules').select('*').execute()
    empty_schedule = { 'M': [], 'T': [], 'W': [], 'Th': [], 'F': [], 'SAT': [], }
    room_schedule = { 'M': [], 'T': [], 'W': [], 'Th': [], 'F': [], 'SAT': [], }


    for schedules in data.data: 
        for schedule in schedules['schedules']:
            schedule_location: str  = schedule['location']
            schedule_location = schedule_location.strip()
            
            if len(schedule_location) > 0 and schedule_location == room_name:
                for day in schedule['days']:
                    room_schedule[day].append({'startTime': schedule['startTime'], 'endTime': schedule['endTime'], 'subject': schedules['description']})

    [room_schedule[day].sort(key=get_time_val) for day in room_schedule]

    if room_schedule == empty_schedule:
        print(room_schedule, '==', empty_schedule)
        return None

    return room_schedule