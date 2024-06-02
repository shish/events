import os
import click
from flask import Flask

from .models import db
from . import models as m
from .utils import htmx
from .routes import index as _index  # just to import the module
from .app import app


def create_app(test_config=None) -> Flask:
    assert _index is not None

    if not os.path.exists("./data"):  # pragma: no cover
        os.makedirs("./data")
    if not os.path.exists("./data/secret.txt"):  # pragma: no cover
        with open("./data/secret.txt", "wb") as fp:
            fp.write(os.urandom(32))
    with open("./data/secret.txt", "rb") as fp2:
        secret_key = fp2.read()
    app.config.from_mapping(
        SECRET_KEY=secret_key,
        SQLALCHEMY_DATABASE_URI="sqlite:///events.sqlite",
    )
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    htmx.init_app(app)

    db.init_app(app)

    @click.command("init-db")
    def init_db_command():  # pragma: no cover
        """Clear the existing data and create new tables."""
        with app.app_context():
            db.drop_all()
            db.create_all()
            admin = m.User("admin", "admin", "admin@example.com")
            persona = m.Persona(name="Mr Admin")
            admin.personas = [persona]
            event = m.Event()
            event.description = "This is a test event"
            event.title = "Test Event"
            event.start_time = db.func.now()
            event.end_time = db.func.now()
            event.owner = persona
            event.tags = [m.Tag("test"), m.Tag("event")]
            db.session.add(admin)
            db.session.add(event)
            db.session.commit()
        click.echo("Initialized the database.")

    app.cli.add_command(init_db_command)

    return app
