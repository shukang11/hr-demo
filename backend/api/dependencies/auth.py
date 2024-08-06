from typing import Annotated, Optional

from fastapi import Depends, Request

from api.error import AuthenticationException
from core.database import AccountInDB
from core.utils import get_logger

from .session import Session

logger = get_logger(__name__)


def _get_token(request: Request) -> Optional[str]:
    auth_content = request.headers.get("Authorization")
    # tirm `Bearer `
    content = auth_content.removeprefix("Bearer ") if auth_content else None
    return content


def get_avaliable_user_if_could(
    session: Session, token: Optional[str] = Depends(_get_token)
) -> Optional[AccountInDB]:
    if not token:
        return None

    user = AccountInDB.find_by_token(session=session, token=token)
    return user


def get_avaliable_user_with_raise(
    session: Session,
    token: Optional[str] = Depends(_get_token),
) -> AccountInDB:
    user = get_avaliable_user_if_could(session=session, token=token)
    if not user:
        raise AuthenticationException("user not found")
    return user


UserOption = Annotated[Optional[AccountInDB], Depends(get_avaliable_user_if_could)]

UserRequire = Annotated[AccountInDB, Depends(get_avaliable_user_with_raise)]
