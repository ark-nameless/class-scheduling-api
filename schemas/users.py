from pydantic import BaseModel, Field, Required, Json


class LoginUser(BaseModel):
    username: str = Field(default=Required)
    password: str = Field(default=Required)

class RequestMessage(BaseModel):
    status: int
    detail: str | dict 