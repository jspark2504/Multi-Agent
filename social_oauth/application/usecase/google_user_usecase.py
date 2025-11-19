from social_oauth.infrastructure.service.GoogleUserService import GoogleUserService
from social_oauth.infrastructure.service.google_oauth2_service import AccessToken
from social_oauth.domain.google_user import GoogleUser

class GoogleUserUseCase:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            google_user_service = GoogleUserService.getInstance()
            cls.__instance = cls(google_user_service)
        return cls.__instance

    def __init__(self, google_user_service: GoogleUserService):
        if hasattr(self, "_initialized") and self._initialized:
            return

        self.google_user_service = google_user_service
        self._initialized = True

    # 토큰 기반 유저 조회/생성
    def fetch_or_create_user_from_token(self, token: AccessToken) -> GoogleUser:
        return self.google_user_service.fetch_or_create_user_from_token(token)

