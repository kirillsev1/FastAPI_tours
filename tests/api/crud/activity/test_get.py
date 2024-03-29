from pathlib import Path

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from tests.conf import URLS

from webapp.crud.utils.operations import PAGE_LIMIT
from webapp.models.sirius.activity import Activity
from webapp.schema.info.activity import ActivityInfo

BASE_DIR = Path(__file__).parent
FIXTURES_PATH = BASE_DIR / 'fixtures'


@pytest.mark.parametrize(
    ('page_id', 'username', 'password', 'expected_status', 'fixtures'),
    [
        (
            '0',
            'test',
            'qwerty',
            status.HTTP_200_OK,
            [
                FIXTURES_PATH / 'sirius.user.json',
                FIXTURES_PATH / 'sirius.tour.json',
                FIXTURES_PATH / 'sirius.activity.json',
            ],
        )
    ],
)
@pytest.mark.asyncio()
@pytest.mark.usefixtures('_common_api_fixture')
async def test_get_activity(
    client: AsyncClient,
    page_id: str,
    username: str,
    password: str,
    expected_status: int,
    access_token: str,
    db_session: AsyncSession,
) -> None:
    response = await client.get(
        ''.join([URLS['crud']['activity'], 'page/', page_id]), headers={'Authorization': f'Bearer {access_token}'}
    )

    activities = [
        ActivityInfo.model_validate(activity).model_dump()
        for activity in (await db_session.scalars(select(Activity).limit(PAGE_LIMIT).offset(int(page_id)))).all()
    ]

    assert activities == response.json()['activity']

    assert response.status_code == expected_status
