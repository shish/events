# mypy: disable-error-code="index"

from sqlalchemy.orm import Session
import pytest
from .. import models as m
from .. import schema as s
from .conftest import Query, Login, Logout
import itertools


@pytest.mark.asyncio
async def test_events_paging(db: Session, query: Query, subtests):
    result = await query("query q { events { title } }")
    assert result.data["events"] == [
        {"title": "Crafty Time"},
        {"title": "Karaoke"},
    ]


@pytest.mark.asyncio
async def test_event_metadata(query: Query):
    result = await query(
        """
        query q {
            event(eventId: 1) {
                id
                title
                description
                tags
                owner {
                    username
                }
            }
        }
    """
    )
    assert result.data["event"] == {
        "id": 1,
        "title": "Crafty Time",
        "description": "Let's meet up and make some stuff",
        "tags": ["online", "social"],
        "owner": {
            "username": "Alice",
        },
    }
