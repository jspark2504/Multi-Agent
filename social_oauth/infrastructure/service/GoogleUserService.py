from social_oauth.adapter.input.web.response.access_token import AccessToken
from social_oauth.domain.google_user import GoogleUser
from social_oauth.infrastructure.repository.google_user_repository_Impl import GoogleUserRepositoryImpl
from social_oauth.infrastructure.service.google_oauth2_service import GoogleOAuth2Service


class GoogleUserService:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    @classmethod
    def getInstance(cls):
        """
        GoogleUserService 싱글톤 인스턴스를 반환.
        내부에서 Repository와 OAuth2Service를 자동으로 DI한다.
        """
        if cls.__instance is None:
            repo = GoogleUserRepositoryImpl()  # RepoImpl 싱글톤 필요 없으면 이렇게 직접 생성
            oauth2_service = GoogleOAuth2Service.getInstance()

            cls.__instance = cls(repo, oauth2_service)

        return cls.__instance

    def __init__(self, google_user_repo=None, oauth2_service=None):
        # __init__ 중복 호출 방지
        if hasattr(self, "_initialized") and self._initialized:
            return

        # 외부 DI 또는 getInstance 자동 DI
        self.google_user_repo = google_user_repo
        self.oauth2_service = oauth2_service

        self._initialized = True

    def fetch_or_create_user_from_token(self, access_token: AccessToken) -> GoogleUser:
        user_profile = self.oauth2_service.fetch_user_profile(access_token)

        google_sub = user_profile["sub"]
        email = user_profile.get("email")
        name = user_profile.get("name")

        user = self.google_user_repo.find_by_google_sub(google_sub)
        if not user:
            user = self.google_user_repo.create(
                google_sub=google_sub,
                email=email,
                name=name,
            )
        return user