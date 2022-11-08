import uuid 
from pydantic import BaseModel, Required, Field



class CreateDepartment(BaseModel):
    name: str = Field(default=Required, min_length=3)
    abbrev: str = Field(default=Required, min_length=2)
    section_id: str = Field(default=Required, min_length=2)
    head_id: str | None = Field(default=None) 


class UpdateDepartment(BaseModel):
    name: str | None = Field(default='')
    abbrev: str | None = Field(default=None)
    section_id: str | None = Field(default=None)
    head_id: str | None = Field(default=None)