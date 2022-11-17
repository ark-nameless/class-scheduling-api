import uuid 
from typing import Union
from pydantic import BaseModel, Required, Field, EmailStr


class Name(BaseModel):
    firstname: Union[str, None] = None
    lastname: Union[str, None] = None
    middlename: Union[str, None] = None

class Address(BaseModel):
    house_no: Union[str, None] = None
    street: Union[str, None] = None
    barangay: Union[str, None] = None
    town: Union[str, None] = None
    province: Union[str, None] = None

class ContactInfo(BaseModel):
    tel_no: Union[str, None] = None
    phone_no: Union[str, None] = None

class PersonalInfo(BaseModel):
    birth_place: Union[str, None] = None
    date_of_birth: Union[str, None] = None
    nationality: Union[str, None] = None
    sex: Union[str, None] = None