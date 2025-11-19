from pydantic import BaseModel


class NicknameSetResponse(BaseModel):
    id: int
    nickname: str
