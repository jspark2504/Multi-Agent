
from typing import Optional
from sqlalchemy.orm import Session

from account.application.port.account_repository_port import AccountRepositoryPort
from config.database.session import get_db_session
from account.domain.account import Account
from account.infrastructure.orm.account_orm import AccountOrm
from account.infrastructure.repository.account_repository import AccountRepository


class AccountRepositoryImpl(AccountRepositoryPort):

    def __init__(self):
        self._SessionLocal = get_db_session

    def _to_domain(self, entity: AccountOrm) -> Account:
        return Account(
            id=entity.id,
            google_sub=entity.google_sub,
            nickname=entity.nickname,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def find_by_google_sub(self, google_sub: str) -> Optional[Account]:
        session: Session = self._SessionLocal()
        try:
            entity = (
                session.query(AccountOrm)
                .filter(AccountOrm.google_sub == google_sub)
                .first()
            )
            return self._to_domain(entity) if entity else None
        finally:
            session.close()

    def find_by_nickname(self, nickname: str) -> Optional[Account]:
        session: Session = self._SessionLocal()
        try:
            entity = (
                session.query(AccountOrm)
                .filter(AccountOrm.nickname == nickname)
                .first()
            )
            return self._to_domain(entity) if entity else None
        finally:
            session.close()

    def save(self, account: Account) -> Account:
        session: Session = self._SessionLocal()
        try:
            if account.id is None:
                entity = AccountOrm(
                    google_sub=account.google_sub,
                    nickname=account.nickname,
                )
                session.add(entity)
                session.commit()
                session.refresh(entity)
            else:
                entity = session.query(AccountORM).get(account.id)
                entity.nickname = account.nickname
                session.commit()
                session.refresh(entity)

            return self._to_domain(entity)
        except:
            session.rollback()
            raise
        finally:
            session.close()
