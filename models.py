from typing import Annotated
from pydantic import BaseModel, HttpUrl, Field, field_validator, EmailStr


BAN_WORDS = {"admin", "root", "moderator", "fuck", "shit", "bitch"}

class CreateURL(BaseModel):
    url: HttpUrl 
    custom_code: str | None = Field(
        default=None,
        pattern=r'^[a-zA-Z0-9]+$',
        min_length=5,
        max_length=10,
        description='буквы от a->z, A->Z и цифры 0->9'
    )
    @field_validator('custom_code')
    @classmethod
    def correct_word(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if v.lower() in BAN_WORDS:
            raise ValueError('вы используете не коректные слова')
        return v
    expires_time: int | None = Field(
        default=None,
        ge=1,
        le=48,
        description='время жизни в часах от 1 до 48 часов. Если не указать,  то будет бесконечная'
    )
    
class URLResponse(BaseModel):
    short_url: str

class User(BaseModel):
    username: str | None = Field(
        default=None,
        pattern=r'^[a-zA-Z0-9]+$',
        min_length=2,
        max_length=10,
        description='Напишите свой ник от 2 до 10 символов'
    )
    email: EmailStr
    password: str = Field(
        min_length=4,
        max_length=28,
        description='Пароль должен быть от 4 до 28 символов'
    )

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str