import uuid
import json

from fastapi import APIRouter, Response, Request, Cookie
from fastapi.responses import RedirectResponse
from starlette.responses import JSONResponse

from config.redis_config import get_redis
from social_oauth.application.usecase.google_oauth2_usecase import GoogleOAuth2UseCase
from social_oauth.infrastructure.repository.google_user_repository import GoogleUserRepository
from social_oauth.infrastructure.service.google_oauth2_service import GoogleOAuth2Service

# 추후 .env로 이동
CLIENT_REDIRECT_URL = "http://localhost:3000"

authentication_router = APIRouter()
service = GoogleOAuth2Service()
google_user_repo = GoogleUserRepository()
usecase = GoogleOAuth2UseCase(service, google_user_repo)
redis_client = get_redis()

@authentication_router.get("/google")
async def redirect_to_google():
    url = usecase.get_authorization_url()
    print("[DEBUG] Redirecting to Google:", url)
    return RedirectResponse(url)


@authentication_router.get("/google/redirect")
async def process_google_redirect(
    response: Response,
    code: str,
    state: str | None = None
):
    print("[DEBUG] /google/redirect called")
    print("code:", code)
    print("state:", state)

    # 1) Google 로그인 → access token + user 정보
    access_token, user = usecase.login_and_fetch_user(state or "", code)
    google_sub = user.sub  # 구글 sub
    # print("[DEBUG] Google sub:", google_sub)

    # 저장할 유저 정보(추후 DB 저장)
    user_data = {
        "sub": google_sub,
        "email": user.email,
        "name": user.name
    }
    # 2) 유저 정보 Redis에 저장
    user_key = f"google:sub:{google_sub}"
    redis_client.set(user_key, json.dumps(user_data, ensure_ascii=False))

    # 3) 세션 생성 및 저장
    session_id = str(uuid.uuid4())
    session_key = f"session:{session_id}"
    print("[DEBUG] Generated session_id:", session_id)
    redis_client.set(session_key, google_sub, ex=3600)
    print("[DEBUG] Session saved in Redis:", redis_client.exists(str(session_key)))

    # 4) 브라우저 쿠키 발급
    redirect_response = RedirectResponse(CLIENT_REDIRECT_URL)
    redirect_response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=False,
        samesite="lax", # none 대신 lax 로(local 용)
        max_age=3600
    )

    print("[DEBUG] Cookie set in RedirectResponse directly")
    return redirect_response

@authentication_router.get("/status")
async def auth_status(request: Request, session_id: str | None = Cookie(None)):
    print("[DEBUG] /status called")

    # 세션 id 없을 경우
    if not session_id:
        print("[DEBUG] No session_id received. Returning logged_in: False")
        return {"logged_in": False}

    # 1) session → sub 조회
    session_key = f"session:{session_id}"
    google_sub = redis_client.get(session_key)

    # sub 없을 경우
    if not google_sub:
        return {"logged_in": False}
    # print("[DEBUG] Raw google_sub from Redis:", google_sub, type(google_sub))

    # bytes 방어
    if isinstance(google_sub, bytes):
        google_sub = google_sub.decode()

    # 2) sub -> 유저 정보 조회
    user_key = f"google:sub:{google_sub}"
    user_json = redis_client.get(user_key)
    # print("[DEBUG] Raw user_json from Redis:", user_json, type(user_json))

    user_info = None
    if user_json:
        if isinstance(user_json, bytes):
            user_json = user_json.decode()
        try:
            user_info = json.loads(user_json)
        except Exception as e:
            print("[ERROR] Failed to parse user_json:", e)

    return {
        "logged_in": True,
        "sub": google_sub,
        "user": user_info,
    }

