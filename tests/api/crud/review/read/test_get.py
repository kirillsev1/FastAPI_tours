from pathlib import Path

import pytest
from httpx import AsyncClient
from starlette import status

from tests.conf import URLS

BASE_DIR = Path(__file__).parent
FIXTURES_PATH = BASE_DIR / 'fixtures'


@pytest.mark.parametrize(
    ('review_id', 'username', 'password', 'expected_status', 'fixtures'),
    [
        (
                '',
                'test',
                'qwerty',
                status.HTTP_200_OK,
                [
                    FIXTURES_PATH / 'sirius.user.json',
                    FIXTURES_PATH / 'sirius.tour.json',
                ],
        ),
        (
                '',
                'test1',
                'qwerty',
                status.HTTP_403_FORBIDDEN,
                [
                    FIXTURES_PATH / 'sirius.user.json',
                    FIXTURES_PATH / 'sirius.tour.json',
                ],
        ),
    ],
)
@pytest.mark.asyncio()
@pytest.mark.usefixtures('_common_api_fixture')
async def test_get(
        client: AsyncClient,
        review_id: str,
        username: str,
        password: str,
        expected_status: int,
        access_token: str,
        db_session: None,
) -> None:
    response = await client.get(
        ''.join([URLS['crud']['review']['read'], review_id]),
        headers={
            'Authorization': f'Bearer {access_token}'
        }
    )

    assert response.status_code == expected_status