import uuid 
from typing import Union
from pydantic import BaseModel, Required, Field, EmailStr

from .general import Name, Address, ContactInfo, PersonalInfo

class Credentials(BaseModel):
    username: Union[str, None] = None
    password: Union[str, None] = None

class TeachingInfo(BaseModel):
    academic_rank: Union[str, None] = None
    teaching_status: Union[str, None] = None
    nature_of_appointment: Union[str, None] = None
    teaching_record: Union[int, None] = None
    other_educational_qualification: Union[str, None] = None

class HighestSchool(BaseModel):
    degree: Union[str, None] = None
    location: Union[str, None] = None

class Consultation(BaseModel):
    time: Union[str, None] = None
    location: Union[str, None] = None

class TeacherInfo(BaseModel):
    profile_img: Union[str, None] =None
    name: Union[Name, None] = None
    address: Union[Address, None] = None
    contact_info: Union[ContactInfo, None] = None
    personal_info: Union[PersonalInfo, None] = None
    teaching_info: Union[TeachingInfo, None] = None
    highest_school: Union[HighestSchool, None] = None
    non_teaching_duty: Union[str, None] = None
    consultation: Union[Consultation, None] = None

class VerifyTeacherAccount(BaseModel):
    user: Union[Credentials, None] = None
    teacher: Union[TeacherInfo, None] = None



class NewUnverifiedTeacher(BaseModel):
    email: EmailStr = Field(default=Required)
    department_id: str = Field(default=Required) 
