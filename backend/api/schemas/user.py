from pydantic import BaseModel, Field


class GetUserSchema(BaseModel):
    id: int
    telegram_id: int
    name: str
    surname: str


class CreateUserSchema(BaseModel):
    chat_id: int = Field(gt=0)
    user_id: int = Field(gt=0)
    name: str = Field(min_length=2, max_length=228)
    username: str = Field(min_length=2, max_length=228)
    
    
