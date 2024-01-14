from fastapi import Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from webapp.api.crud.review.router import review_router
from webapp.crud.review import review_crud
from webapp.integrations.cache.cache import redis_drop_key
from webapp.integrations.postgres import get_session
from webapp.models.sirius.review import Review
from webapp.utils.auth.jwt import JwtTokenT, jwt_auth


@review_router.delete('/{review_id}')
async def delete_review(
    review_id: int,
    session: AsyncSession = Depends(get_session),
    access_token: JwtTokenT = Depends(jwt_auth.validate_token),
) -> Response:
    if not await review_crud.delete(session, review_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    await redis_drop_key(Review.__name__, review_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
