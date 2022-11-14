from pydantic import BaseModel, Field, Required, Json
from typing import Union



class AuthVerification(BaseModel):
    id: str = Field(default=Required)
    
class LoginUser(BaseModel):
    username: str = Field(default=Required)
    password: str = Field(default=Required)

class RequestMessage(BaseModel):
    status: int
    detail: Union[str, dict]