from typing import Tuple
from social_oauth.infrastructure.repository.google_user_repository import GoogleUserRepository
from social_oauth.infrastructure.service.google_oauth2_service import (
    GoogleOAuth2Service,
    GetAccessTokenRequest,
    AccessToken,
)
from social_oauth.domain.google_user import GoogleUser

class GoogleOAuth2UseCase:
    def __init__(self, service: GoogleOAuth2Service, google_user_repo: GoogleUserRepository):
        self.service = service
        self.google_user_repo = google_user_repo

    def get_authorization_url(self) -> str:
        return self.service.get_authorization_url()

    def login_and_fetch_user(self, state: str, code: str) -> Tuple[AccessToken, GoogleUser]:
        token_request = GetAccessTokenRequest(state=state, code=code)

        # 1. 토큰 발급
        access_token = self.service.refresh_access_token(token_request)

        # 2. 프로필 조회
        user_profile = self.service.fetch_user_profile(access_token)
        # print("[DEBUG] Full user_profile response:", user_profile)

        google_sub = user_profile["sub"]
        email = user_profile.get("email")
        name = user_profile.get("name")

        # 3. 유저 조회 또는 생성 (추후 DB연동을 위해 email, name 필요)
        user = self.google_user_repo.find_by_google_sub(google_sub)
        if not user:
            user = self.google_user_repo.create(
                google_sub=google_sub,
                email=email,
                name=name,
            )

        # 4. 토큰 + 유저 둘 다 반환
        return access_token, user