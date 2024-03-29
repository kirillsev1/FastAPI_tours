from pathlib import Path

import pytest
from httpx import AsyncClient
from starlette import status

from tests.conf import URLS

from webapp.integrations.cache.cache import redis_get
from webapp.models.sirius.review import Review

BASE_DIR = Path(__file__).parent
FIXTURES_PATH = BASE_DIR / 'fixtures'


@pytest.mark.parametrize(
    ('review_id', 'username', 'password', 'expected_status', 'fixtures'),
    [
        (
            '0',
            'test',
            'qwerty',
            status.HTTP_200_OK,
            [
                FIXTURES_PATH / 'sirius.user.json',
                FIXTURES_PATH / 'sirius.tour.json',
                FIXTURES_PATH / 'sirius.review.json',
            ],
        ),
    ],
)
@pytest.mark.asyncio()
@pytest.mark.usefixtures('_common_api_with_redis_fixture')
async def test_cache_review(
    client: AsyncClient,
    review_id: str,
    expected_status: int,
    access_token: str,
    db_session: None,
) -> None:
    response = await client.get(
        ''.join([URLS['crud']['review'], review_id]), headers={'Authorization': f'Bearer {access_token}'}
    )

    assert response.status_code == expected_status

    assert await redis_get(Review.__name__, review_id)
