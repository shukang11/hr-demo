from typing import Optional

from extensions.ext_database import db
from libs.helper import getmd5
from models.account import AccountInDB, AccountTokenInDB
from sqlalchemy import select
from sqlalchemy.orm import joinedload


class AccountService:
    @staticmethod
    def find_account_by_id(id: int) -> Optional[AccountInDB]:
        # session in UserInDB
        session = db.session
        stmt = (
            select(AccountInDB)
            .options(joinedload(AccountInDB.token))
            .where(AccountInDB.id == id)
        )
        user = session.execute(stmt).scalar_one_or_none()
        return user

    @staticmethod
    def is_account_exists(username: str) -> bool:
        session = db.session
        stmt = select(AccountInDB).where(AccountInDB.username == username)
        user = session.execute(stmt).scalar_one_or_none()
        return user is not None

    @staticmethod
    def find_account_by_token(token: str) -> Optional[AccountInDB]:
        session = db.session
        stmt = (
            select(AccountInDB)
            .options(joinedload(AccountInDB.token))
            .where(AccountTokenInDB.token == token)
        )
        user = session.execute(stmt).scalar_one_or_none()
        return user

    @staticmethod
    def find_account_by_login(username: str, password: str) -> Optional[AccountInDB]:
        hashed_password = password
        session = db.session
        stmt = (
            select(AccountInDB)
            .options(joinedload(AccountInDB.token))
            .where(
                AccountInDB.username == username,
                AccountInDB.password == hashed_password,
            )
        )
        user = session.execute(stmt).scalar_one_or_none()
        return user

    @staticmethod
    def create_account_token(user_id: int, token: str) -> AccountTokenInDB:
        user_token = AccountTokenInDB(account_id=user_id, token=token)
        db.session.add(user_token)
        db.session.flush()
        return user_token

    @staticmethod
    def get_account_token(account: AccountInDB, salt: str) -> str:
        if account.token:
            return account.token.token
        new_token = account.make_new_token_value(salt=salt)
        account_token = AccountTokenInDB(account_id=account.id, token=new_token)
        db.session.add(account_token)
        db.session.flush()
        return new_token

    @staticmethod
    def create_account_if_counld(
        username: str,
        password: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
    ) -> AccountInDB:
        account = AccountInDB()
        account.username = username
        if email:
            account.email = email
        if phone:
            account.phone = phone

        password_hashed = getmd5(password)
        account.password = password_hashed

        db.session.add(account)
        db.session.flush()
        return account

    @staticmethod
    def update_account_token(account: AccountInDB, salt: str) -> str:
        # find old token
        new_token = account.make_new_token_value(salt=salt)
        account.token.token = new_token
        db.session.add(account)
        return new_token
