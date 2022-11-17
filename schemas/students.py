import uuid 
from typing import Union
from pydantic import BaseModel, Required, Field, EmailStr

from .general import Name, Address, ContactInfo, PersonalInfo


class SchoolInfo(BaseModel):
    name: Union[str, None] = None
    location: Union[str, None] = None
    year: Union[str, None] = None

class Credentials(BaseModel):
    username: Union[str, None] = None
    password: Union[str, None] = None

class ParentInfo(BaseModel):
    father: Union[Name, None] = None
    mother: Union[Name, None] = None
    guardian: Union[Name, None] = None


class SchoolingInfo(BaseModel):
    elem: Union[SchoolInfo, None] = None
    junior_high: Union[SchoolInfo, None] = None
    senior_high: Union[SchoolInfo, None] = None

class LearnerInfo(BaseModel):
    is_transfer: Union[bool, None] = False
    college_name: Union[str, None] = None 
    lrn: Union[str, None] = None
class StudentInfo(BaseModel):
    profile_img: Union[str, None] =None
    name: Union[Name, None] = None
    address: Union[Address, None] = None
    contact_info: Union[ContactInfo, None] = None
    personal_info: Union[PersonalInfo, None] = None
    parent_info: Union[ParentInfo, None] = None 
    schooling_info: Union[SchoolingInfo, None] = None
    learner_info: Union[LearnerInfo, None] = None

class VerifyStudentAccount(BaseModel):
    user: Union[Credentials, None] = None
    student: Union[StudentInfo, None] = None


class NewUnverifiedStudent(BaseModel):
    email: EmailStr = Field(default=Required)
    department_id: str = Field(default=Required) 
