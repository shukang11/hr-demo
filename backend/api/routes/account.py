from fastapi import APIRouter

from api.dependencies.auth import UserRequire
from api.dependencies.session import Session
from api.response import Response
from core.controller.account import (
    LoginAccountResp,
    LoginAccountPayload,
    InsertAccountPayload,
    AccountSchema,
    AccountManager,
)
from core.utils import settings


router = APIRouter(prefix="/auth", tags=["个人信息接口"])


@router.post(
    "/register",
    summary="注册",
    description="注册用户",
    response_model=Response[int],
)
async def _register_user(req: InsertAccountPayload, session: Session) -> Response[int]:
    if not any([req.username, req.phone, req.email]):
        return Response.from_error(message=" 邮箱 不能同时为空")
    req.id = None
    req.phone = None
    req.username = None
    try:
        manager = AccountManager(session=session)
        user = manager.create_account(payload=req, settings=settings)
        return Response(data=user.id)
    except Exception as e:
        return Response.from_error(f"{e}")


@router.post(
    "/login",
    summary="登录",
    description="登录",
    response_model=Response[LoginAccountResp],
)
async def _user_login(
    req: LoginAccountPayload, session: Session
) -> Response[LoginAccountResp]:
    try:
        manager = AccountManager(session=session)
        user = manager.login_account(payload=req, settings=settings)
        if not user:
            return Response.from_error(message="login failed")
        resp = LoginAccountResp(
            token=user.token.token, user=AccountSchema.model_validate(user)
        )
        return Response(data=resp)
    except Exception as e:
        return Response.from_error(f"{e}")


@router.post(
    "/info",
    summary="用户信息",
    description="获得用户信息",
    response_model=Response[AccountSchema],
)
async def customer_info(
    user: UserRequire,
) -> Response[AccountSchema]:
    u = AccountSchema.model_validate(user)
    return Response(data=u)


@router.post(
    "/logout",
    summary="登出",
    description="登出",
    response_model=Response[bool],
)
async def user_logout(user: UserRequire, session: Session) -> Response[bool]:
    manager = AccountManager(session=session)
    manager.logout_account(user)
    return Response(data=True)
