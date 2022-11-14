import uuid 
from pydantic import BaseModel, Required, Field, EmailStr



class NewUnverifiedTeacher(BaseModel):
    email: EmailStr = Field(default=Required)
    department_id: str = Field(default=Required) 
