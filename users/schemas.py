from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Annotated
from annotated_types import MinLen, MaxLen


class CreateUser(BaseModel):
    # username: str = Field(..., min_items=3, max_length=20)
    username: Annotated[str, MaxLen(20), MinLen(3)]
    email: EmailStr


class UserSchema(BaseModel):
    model_config = ConfigDict(strict=True)

    username: str
    password: bytes
    email: EmailStr | None = None
    active: bool = True
