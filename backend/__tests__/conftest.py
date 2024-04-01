from flask import Flask
from flask.ctx import AppContext
from flask.sessions import SecureCookieSession
from flask.testing import FlaskClient
from flask_sqlalchemy import SQLAlchemy
from strawberry_sqlalchemy_mapper import StrawberrySQLAlchemyLoader  # type: ignore
from graphql import ExecutionResult
import pytest
import typing as t

from .. import schema as s
from .. import models as m
from ..app import create_app


"""
import dataclasses

@dataclasses.dataclass
class TestCtx:
    app: Flask
    client: FlaskClient
    ctx: AppContext
    db: SQLAlchemy
    cookie: SecureCookieSession
"""
@pytest.fixture
def app() -> Flask:
    return create_app(
        test_config={
            "DATABASE_URL": "sqlite:///:memory:",
            "DATABASE_ECHO": True,
        }
    )

@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()

@pytest.fixture
def db(app: Flask) -> t.Generator[SQLAlchemy, t.Any, t.Any]:
    with app.app_context():
        m.SECURE = False
        m.db.drop_all()
        m.db.create_all()
        m.populate_example_data(m.db)
        yield m.db

@pytest.fixture
def cookie() -> SecureCookieSession:
    return SecureCookieSession()


class Query(t.Protocol):
    def __call__(
        self, q: str, error: t.Optional[str] = None, **kwargs
    ) -> t.Coroutine[t.Any, t.Any, ExecutionResult]:  # pragma: no cover
        ...


@pytest.fixture
def query(db, cookie) -> Query:
    async def _query(q, error: t.Optional[str] = None, **kwargs):
        gqlctx: s.Context = {
            "db": db,
            "cookie": cookie,
            "cache": {},
            "sqlalchemy_loader": StrawberrySQLAlchemyLoader(bind=db.session),
        }
        result = await s.schema.execute(
            q,
            context_value=gqlctx,
            variable_values=kwargs,
        )
        if error:
            assert result.errors is not None
            assert result.errors[0].message == error
        else:
            assert result.errors is None, result.errors
        return result

    return _query


class Login(t.Protocol):
    def __call__(
        self, username: str = "alice", password: t.Optional[str] = None
    ) -> t.Coroutine[t.Any, t.Any, ExecutionResult]:  # pragma: no cover
        ...


@pytest.fixture
def login(query) -> Login:
    return lambda username="alice", password=None: query(
        """
        mutation m($username: String!, $password: String!) {
            login(username: $username, password: $password) {
                username
            }
        }
    """,
        username=username,
        password=password or username.lower() + "pass",
    )


class Logout(t.Protocol):
    def __call__(
        self,
    ) -> t.Coroutine[t.Any, t.Any, ExecutionResult]:  # pragma: no cover
        ...


@pytest.fixture
def logout(query) -> Logout:
    return lambda: query("mutation m { logout }")
