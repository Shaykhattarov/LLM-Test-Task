from pydantic import BaseModel, Field


class CreateMessageSchema(BaseModel):
    user_id: int
    text: str = Field(min_length=2, max_length=4096)
