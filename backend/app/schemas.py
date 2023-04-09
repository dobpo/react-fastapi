import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, constr
from app.common.schemas import CamelSchema


class UserBaseSchema(CamelSchema):
    name: str
    email: EmailStr | None
    is_superuser: bool

    class Config:
        orm_mode = True


class CreateUserSchema(UserBaseSchema):
    password: constr(min_length=4)


class LoginUserSchema(BaseModel):
    name: str
    password: constr(min_length=4)


class LoginUserResponse(CamelSchema):
    status: str
    is_superuser: bool
    access_token: str


class UserResponse(UserBaseSchema):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
