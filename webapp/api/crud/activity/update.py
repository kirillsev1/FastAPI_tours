from fastapi import Depends, HTTPException
from fastapi.responses import ORJSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from webapp.api.crud.router import crud_router
from webapp.crud.activity import activity_crud
from webapp.integrations.postgres import get_session
from webapp.schema.info.activity import ActivityInfo
from webapp.utils.auth.jwt import JwtTokenT, jwt_auth


@crud_router.get('/activity/update')
async def get_activity(
    body: ActivityInfo,
    activity_id: int,
    session: AsyncSession = Depends(get_session),
    access_token: JwtTokenT = Depends(jwt_auth.validate_token),
) -> ORJSONResponse:
    activity = await activity_crud.get(session, activity_id)  # type: ignore
    if activity is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    await activity_crud.update(session, activity_id, body)

    return ORJSONResponse(content={'message': 'Activity removed successfully'}, status_code=status.HTTP_204_NO_CONTENT)
