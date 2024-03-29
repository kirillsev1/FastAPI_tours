from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.responses import ORJSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from webapp.api.crud.user.router import user_router
from webapp.crud.user import user_crud
from webapp.integrations.cache.cache import redis_get, redis_set
from webapp.integrations.postgres import get_session
from webapp.models.sirius.user import User
from webapp.schema.info.user import UserInfo
from webapp.utils.auth.jwt import oauth2_scheme


@user_router.get('/page/{page}')
async def get_users(
    page: int,
    access_token: Annotated[OAuth2PasswordRequestForm, Depends(oauth2_scheme)],
    session: AsyncSession = Depends(get_session),
) -> ORJSONResponse:
    serialized_users = [UserInfo.model_validate(user).model_dump() for user in await user_crud.get_page(session, page)]
    return ORJSONResponse({'users': serialized_users})


@user_router.get('/{user_id}')
async def get_cached_user(
    user_id: int,
    access_token: Annotated[OAuth2PasswordRequestForm, Depends(oauth2_scheme)],
    session: AsyncSession = Depends(get_session),
) -> ORJSONResponse:
    if cached := (await redis_get(User.__name__, user_id)):
        return ORJSONResponse({'user': cached})

    user = await user_crud.get_model(session, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    serialized_user = UserInfo.model_validate(user).model_dump(mode='json')
    await redis_set(User.__name__, user_id, serialized_user)

    return ORJSONResponse({'user': serialized_user})
