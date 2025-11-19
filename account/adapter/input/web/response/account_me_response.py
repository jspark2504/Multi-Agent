from pydantic import BaseModel
from typing import Optional


class AccountMeResponse(BaseModel):
    nickname: Optional[str] = None
    has_nickname: bool
    can_set_nickname: bool
