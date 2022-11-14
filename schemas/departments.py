import uuid 
from typing import Optional
from pydantic import BaseModel, Required, Field



class CreateDepartment(BaseModel):
    name: str = Field(default=Required, min_length=3)
    abbrev: str = Field(default=Required, min_length=2)
    section_id: str = Field(default=Required, min_length=2)
    head_id: Optional[str] = Field(default=None) 


class UpdateDepartment(BaseModel):
    name: Optional[str] = Field(default='')
    abbrev: Optional[str] = Field(default=None)
    section_id: Optional[str] = Field(default=None)
    head_id: Optional[str] = Field(default=None)