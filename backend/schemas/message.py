
from typing import Optional, List, Any
from pydantic import BaseModel, Field


class CreateMessageSchema(BaseModel):
    user_id: int 
    text: str = Field(min_length=1, max_length=4096)
    status: str

class UpdateMessageSchema(BaseModel):
    id: int
    user_id: int
    text: Optional[str]
    status: Optional[str]
    created_at: Optional[Any]

class MessageSchema(BaseModel):
    id: int
    user_id: int
    text: str
    status: Any
    created_at: Any
    
    
class EditModelAnswerSchema(BaseModel):
    id: int
    text: str