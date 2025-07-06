from pydantic import BaseModel


class GetUserSchema(BaseModel):
    id: int
    telegram_id: int
    name: str
    surname: str
