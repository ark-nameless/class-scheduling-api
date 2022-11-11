import uuid 
from pydantic import BaseModel, Required, Field, EmailStr



class NewUnverifiedStudent(BaseModel):
    email: EmailStr = Field(default=Required)
    department_id: str = Field(default=Required) 
