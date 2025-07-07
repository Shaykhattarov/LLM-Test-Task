from pydantic import BaseModel, Field


class CreateMessageSchema(BaseModel):
    user_id: int 
    text: str = Field(min_length=1, max_length=2000)
    status: str
    
