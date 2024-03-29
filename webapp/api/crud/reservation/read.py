from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.responses import ORJSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from webapp.api.crud.reservation.router import reservation_router
from webapp.crud.reservation import reservation_crud
from webapp.integrations.cache.cache import redis_get, redis_set
from webapp.integrations.postgres import get_session
from webapp.models.sirius.reservation import Reservation
from webapp.schema.info.reservation import ReservationInfo
from webapp.utils.auth.jwt import oauth2_scheme


@reservation_router.get('/page/{page}')
async def get_reservations(
    page: int,
    access_token: Annotated[OAuth2PasswordRequestForm, Depends(oauth2_scheme)],
    session: AsyncSession = Depends(get_session),
) -> ORJSONResponse:
    serialized_reservations = [
        ReservationInfo.model_validate(reservation).model_dump()
        for reservation in await reservation_crud.get_page(session, page)
    ]
    return ORJSONResponse({'reservations': serialized_reservations})


@reservation_router.get('/{reservation_id}')
async def get_cached_reservation(
    reservation_id: int,
    access_token: Annotated[OAuth2PasswordRequestForm, Depends(oauth2_scheme)],
    session: AsyncSession = Depends(get_session),
) -> ORJSONResponse:
    if cached := (await redis_get(Reservation.__name__, reservation_id)):
        return ORJSONResponse({'reservation': cached})

    reservation = await reservation_crud.get_model(session, reservation_id)
    if reservation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    serialized_reservation = ReservationInfo(**reservation.__dict__).model_dump(mode='json')
    await redis_set(Reservation.__name__, reservation_id, serialized_reservation)

    return ORJSONResponse({'reservation': serialized_reservation})
