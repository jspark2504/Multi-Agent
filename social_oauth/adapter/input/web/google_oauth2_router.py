import uuid

from fastapi import APIRouter, Response, Request, Cookie
from fastapi.responses import RedirectResponse
from starlette.responses import JSONResponse

from config.redis_config import get_redis
from social_oauth.application.usecase.google_oauth2_usecase import GoogleOAuth2UseCase
from social_oauth.application.usecase.google_user_usecase import GoogleUserUseCase

# 추후 .env로 이동
CLIENT_REDIRECT_URL = "http://localhost:3000"

authentication_router = APIRouter()

oauth_usecase = GoogleOAuth2UseCase.getInstance()
user_usecase = GoogleUserUseCase.getInstance()
redis_client = get_redis()


@authentication_router.get("/google")
async def redirect_to_google():
    url = oauth_usecase.get_authorization_url()
    print("[DEBUG] Redirecting to Google:", url)
    return RedirectResponse(url)


@authentication_router.get("/google/redirect")
async def process_google_redirect(
    response: Response,
    code: str,
    state: str | None = None,
):
    print("[DEBUG] /google/redirect called")
    print("code:", code)
    print("state:", state)

    # 1) AccessToken 발급
    access_token = oauth_usecase.issue_access_token(state or "", code)
    print("[DEBUG] Access token received:", access_token.access_token)

    # 2) 유저 조회/생성 (google_user 테이블 저장)
    user = user_usecase.fetch_or_create_user_from_token(access_token)

    # 3) 세션 ID 생성
    session_id = str(uuid.uuid4())
    google_sub = user.sub
    print("[DEBUG] Generated session_id:", session_id)

    # 4) Redis에 "세션ID → access_token" 형태로만 저장 (1시간 TTL)
    #    (기존 as-is 로직과 동일한 형태로 복원)
    redis_client.set(session_id, access_token.access_token, ex=3600)
    print("[DEBUG] Session saved in Redis:", redis_client.exists(session_id))

    # 4-1) redis에 google_sub 저장(DB 조회 용)
    session_key = f"session:{session_id}"
    redis_client.set(session_key, google_sub, ex=3600)

    # 5) 브라우저 쿠키에 세션ID 심기
    redirect_response = RedirectResponse(CLIENT_REDIRECT_URL)
    redirect_response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=False,  # local용
        samesite="lax",  # local용
        max_age=3600,
    )
    print("[DEBUG] Cookie set in RedirectResponse directly")

    return redirect_response


@authentication_router.get("/status")
async def auth_status(
    request: Request,
    session_id: str | None = Cookie(None),
):
    print("[DEBUG] /status called")
    print("[DEBUG] Received session_id cookie:", session_id)

    # 1) 세션 ID 자체가 없으면 비로그인
    if not session_id:
        print("[DEBUG] No session_id received. Returning logged_in: False")
        return {"logged_in": False}

    # 2) Redis에 해당 세션ID가 존재하는지만 확인
    exists = redis_client.exists(session_id)
    print("[DEBUG] Redis has session_id?", exists)

    return {"logged_in": bool(exists)}


@authentication_router.post("/logout")
async def logout(session_id: str | None = Cookie(None)):
    print("[DEBUG] /logout called. session_id:", session_id)

    # 1) 세션 ID가 있으면 Redis에서 삭제
    if session_id:
        try:
            deleted = redis_client.delete(session_id)
            print("[DEBUG] Deleted session in Redis:", session_id, "result:", deleted)
        except Exception as e:
            print("[ERROR] Failed to delete session in Redis:", e)

    # 2) 응답 + 쿠키 삭제
    response = JSONResponse({"logged_in": False})
    response.delete_cookie("session_id")

    return response
