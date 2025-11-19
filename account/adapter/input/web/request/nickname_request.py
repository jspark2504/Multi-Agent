from pydantic import BaseModel


class NicknameRequest(BaseModel):
    nickname: str