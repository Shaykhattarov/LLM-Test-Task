from pydantic import BaseModel, Field


class CreateMessageSchema(BaseModel):
    user_id: int 
    text: str = Field(min_length=1, max_length=4096)
    status: str
    
