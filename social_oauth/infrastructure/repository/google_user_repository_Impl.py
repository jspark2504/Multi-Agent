
from typing import Optional

from sqlalchemy.orm import Session

from social_oauth.domain.google_user import GoogleUser
from social_oauth.infrastructure.orm.google_user_orm import GoogleUserOrm
from social_oauth.infrastructure.repository.google_user_repository import GoogleUserRepository
from config.database.session import get_db_session


class GoogleUserRepositoryImpl(GoogleUserRepository):

    def __init__(self):
        # 세션 팩토리 가져오기
        self._SessionLocal = get_db_session

    def _to_domain(self, entity: GoogleUserOrm) -> GoogleUser:
        user = GoogleUser(
            sub=entity.sub,
            email=entity.email,
            name=entity.name,
        )
        user.created_at = entity.created_at
        user.updated_at = entity.updated_at
        return user

    def find_by_google_sub(self, google_sub: str) -> Optional[GoogleUser]:
        session: Session = self._SessionLocal()
        try:
            entity = (
                session.query(GoogleUserOrm)
                .filter(GoogleUserOrm.sub == google_sub)
                .first()
            )

            if not entity:
                return None

            return self._to_domain(entity)

        finally:
            session.close()

    def create(self, google_sub: str, email: str, name: Optional[str] = None) -> GoogleUser:
        session: Session = self._SessionLocal()
        try:
            entity = GoogleUserOrm(
                sub=google_sub,
                email=email,
                name=name,
            )

            session.add(entity)
            session.commit()
            session.refresh(entity)

            return self._to_domain(entity)

        except:
            session.rollback()
            raise

        finally:
            session.close()