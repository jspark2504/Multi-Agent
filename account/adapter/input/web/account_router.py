from typing import Optional

from fastapi import APIRouter, Cookie, Depends, HTTPException, status
from starlette.responses import JSONResponse
from pydantic import BaseModel
from account.adapter.input.web.request.nickname_request import NicknameRequest
from account.adapter.input.web.response.account_me_response import AccountMeResponse
from account.adapter.input.web.response.nickname_check_response import NicknameCheckResponse
from account.adapter.input.web.response.nickname_set_response import NicknameSetResponse

from account.application.usecase.account_usecase import AccountUseCase
from config.redis_config import get_redis

account_router = APIRouter(prefix="/account", tags=["account"])
account_usecase = AccountUseCase.getInstance()
redis_client = get_redis()


class NicknameRequest(BaseModel):
    nickname: str


def get_current_google_sub(session_id: Optional[str] = Cookie(None)) -> str:
    """
    세션 ID → Redis → google_sub 조회 공통 의존성
    - 세션 ID 없거나 Redis에 키 없으면 401 에러
    """
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="로그인이 필요합니다.",
        )

    # /google/redirect 쪽에서 사용하는 키 형식이랑 반드시 맞춰줄 것!
    session_key = f"session:{session_id}"   # 예: "session:xxxx-xxxx-..."
    google_sub = redis_client.get(session_key)

    if not google_sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="세션이 유효하지 않습니다.",
        )

    if isinstance(google_sub, bytes):
        google_sub = google_sub.decode()

    return google_sub


@account_router.get("/me", response_model=AccountMeResponse)
async def get_my_account(google_sub: str = Depends(get_current_google_sub)):
    return account_usecase.get_my_account(google_sub)

@account_router.post("/nickname/check", response_model=NicknameCheckResponse)
async def check_nickname(body: NicknameRequest):
    available = account_usecase.check_nickname_available(body.nickname)
    return NicknameCheckResponse(available=available)


@account_router.post("/nickname", response_model=NicknameSetResponse)
async def set_nickname(
    body: NicknameRequest,
    google_sub: str = Depends(get_current_google_sub),
):
    try:
        return account_usecase.set_my_nickname(google_sub, body.nickname)
    except ValueError as e:
        return JSONResponse({"detail": str(e)}, status_code=400)
