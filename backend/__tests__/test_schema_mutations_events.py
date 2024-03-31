# mypy: disable-error-code="index"

from sqlalchemy.orm import Session
import pytest
from .. import models as m
from .conftest import Query, Login


@pytest.mark.asyncio
async def test_createEvent(db: Session, query: Query, login: Login, subtests):
    CREATE_EVENT = """
        mutation m {
            createEvent(
                event: {
                    title: "TestTitle"
                    description: "TestDesc"
                    tags: ["social", "sober"],
                    startTime: "2021-01-01T00:00:00",
                    endTime: "2021-01-01T01:00:00",
                }
            ) {
                id
            }
        }
    """

    with subtests.test("anon"):
        # anon can't create a survey
        result = await query(CREATE_EVENT, error="Anonymous users can't create events")
        assert result.data is None

    with subtests.test("user"):
        # log in
        await login()

        # logged in can create a survey
        result = await query(CREATE_EVENT)
        assert result.data["createEvent"]["id"] is not None

        # check the survey was created
        event = (
            db.query(m.Event)
            .filter(m.Event.id == result.data["createEvent"]["id"])
            .one()
        )
        assert event.title == "TestTitle"
        assert event.description == "TestDesc"
        assert event.owner.username == "Alice"
