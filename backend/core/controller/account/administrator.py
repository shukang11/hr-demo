from typing import Optional
from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from core.controller._base import BaseController
from core.database import AdministratorInDB, AdministratorTokenInDB
from .schema import InsertAccountPayload, LoginAccountPayload


class AccountManager(BaseController):
    def __init__(self, session: Session) -> None:
        self.session = session

    def insert_administrator(
        self, /, payload: InsertAccountPayload, scret: Optional[str] = None
    ) -> AdministratorInDB:
        session = self.session

        # 查询是否存在的条件
        insert_account: AdministratorInDB
        if payload.id:
            stmt = select(AdministratorInDB).where(AdministratorInDB.id == payload.id)
            if not session.scalar(stmt):
                raise ValueError("用户不存在")
            insert_account = AdministratorInDB.find_by_id(session, payload.id)
        elif any([payload.username, payload.phone, payload.email]):
            stmt = (
                select(AdministratorInDB)
                .options(joinedload(AdministratorInDB.token))
                .where(
                    or_(
                        AdministratorInDB.username == payload.username,
                        AdministratorInDB.phone == payload.phone,
                        AdministratorInDB.email == payload.email,
                    )
                )
                .where(AdministratorInDB.password == payload.password)
            )
            if session.scalar(stmt):
                raise ValueError("用户已存在")
            insert_account = AdministratorInDB(
                username=payload.username,
                phone=payload.phone,
                email=payload.email,
                password=payload.password,
            )
            new_token_value = insert_account.make_new_token(scret)
            insert_account.token = AdministratorTokenInDB(
                admin_id=insert_account.id, value=new_token_value
            )

        if not insert_account:
            raise ValueError("用户不存在")

        if payload.username:
            insert_account.username = payload.username
        if payload.phone:
            insert_account.phone = payload.phone
        if payload.email:
            insert_account.email = payload.email
        session.add(insert_account)

        return insert_account

    def login_administrator(
        self, /, payload: LoginAccountPayload, scret: str
    ) -> AdministratorInDB:
        session = self.session
        stmt = (
            select(AdministratorInDB)
            .options(joinedload(AdministratorInDB.token))
            .where(
                AdministratorInDB.email == payload.email,
                AdministratorInDB.password == payload.password,
            )
        )
        result = session.execute(stmt)

        account = result.scalar()

        if not account:
            raise ValueError("用户名或密码错误")

        # 更新用户token

        new_token = account.make_new_token(scret)
        account.token.value = new_token
        session.add(account)

        return account

    def logout_administrator(self, /, account: AdministratorInDB) -> bool:
        session = self.session
        self.session.delete(account.token)
        session.commit()
        return True
