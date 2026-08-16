import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.generated_episode_repository import GeneratedEpisodeRepository


def _episode_kwargs(theme_id: str = "paylasma") -> dict[str, Any]:
    return {
        "theme_id": theme_id,
        "theme_label": "Paylaşma",
        "title": "Neşeli Orman: Paylaşma",
        "lead_character_id": "findik",
        "support_character_id": "boncuk",
        "location_id": "paylasim_bahcesi",
        "lesson": "Paylaşmak çoğaltır.",
        "scenes": [
            {
                "name": "Açılış",
                "duration_seconds": 30,
                "text": "...",
                "speaker": None,
                "dialogue": None,
            }
        ],
        "seo_package": {
            "titles": ["t1"],
            "description": "d",
            "tags": ["a"],
            "thumbnail_suggestion": "s",
        },
        "shorts_plan": {"episode_theme_id": theme_id, "segments": [], "total_duration_seconds": 0},
    }


async def test_create_persists_and_returns_a_row_with_generated_id_and_timestamp(
    db_session: AsyncSession,
) -> None:
    repository = GeneratedEpisodeRepository(db_session)

    record = await repository.create(**_episode_kwargs())

    assert isinstance(record.id, uuid.UUID)
    assert record.created_at is not None
    assert record.title == "Neşeli Orman: Paylaşma"


async def test_get_by_id_returns_none_for_an_unknown_id(db_session: AsyncSession) -> None:
    repository = GeneratedEpisodeRepository(db_session)

    assert await repository.get_by_id(uuid.uuid4()) is None


async def test_get_by_id_returns_the_persisted_row(db_session: AsyncSession) -> None:
    repository = GeneratedEpisodeRepository(db_session)
    created = await repository.create(**_episode_kwargs())

    fetched = await repository.get_by_id(created.id)

    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.scenes == created.scenes


async def test_list_paginated_orders_newest_first_and_reports_total(
    db_session: AsyncSession,
) -> None:
    repository = GeneratedEpisodeRepository(db_session)
    first = await repository.create(**_episode_kwargs("paylasma"))
    second = await repository.create(**_episode_kwargs("aile"))
    third = await repository.create(**_episode_kwargs("cesaret"))

    rows, total = await repository.list_paginated(page=1, page_size=2)

    assert total == 3
    assert [row.id for row in rows] == [third.id, second.id]
    assert first.id not in [row.id for row in rows]


async def test_list_paginated_second_page_returns_the_remainder(db_session: AsyncSession) -> None:
    repository = GeneratedEpisodeRepository(db_session)
    first = await repository.create(**_episode_kwargs("paylasma"))
    await repository.create(**_episode_kwargs("aile"))
    await repository.create(**_episode_kwargs("cesaret"))

    rows, total = await repository.list_paginated(page=2, page_size=2)

    assert total == 3
    assert [row.id for row in rows] == [first.id]


async def test_delete_removes_the_row_and_reports_success(db_session: AsyncSession) -> None:
    repository = GeneratedEpisodeRepository(db_session)
    created = await repository.create(**_episode_kwargs())

    deleted = await repository.delete(created.id)

    assert deleted is True
    assert await repository.get_by_id(created.id) is None


async def test_delete_returns_false_for_an_unknown_id(db_session: AsyncSession) -> None:
    repository = GeneratedEpisodeRepository(db_session)

    assert await repository.delete(uuid.uuid4()) is False
