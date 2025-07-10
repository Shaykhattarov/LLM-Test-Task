from typing import Any
from pydantic import BaseModel


class AnswerSchema(BaseModel):
    id: int
    message_id: int
    text: str
    created_at: Any