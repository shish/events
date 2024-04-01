from flask import Flask, Request, Response, session, jsonify
from strawberry.flask.views import AsyncGraphQLView
from strawberry_sqlalchemy_mapper import StrawberrySQLAlchemyLoader  # type: ignore
import os
import datetime
import click
from sqlalchemy import select

from . import schema as s
from . import models as m


class MyGraphQLView(AsyncGraphQLView):
    async def get_context(self, request: Request, response: Response) -> s.Context:
        return {
            "db": m.db,
            "cookie": session,
            "cache": {},
            "sqlalchemy_loader": StrawberrySQLAlchemyLoader(bind=m.db.session),
        }


def create_app(test_config=None):
    ###################################################################
    # Load config

    app = Flask(
        __name__,
        instance_path=os.path.abspath("./data"),
        static_folder="../frontend/dist",
    )
    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI="sqlite:///events.sqlite",
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_SAMESITE="None",
        PERMANENT_SESSION_LIFETIME=datetime.timedelta(days=365),
    )
    if test_config is None:  # pragma: no cover
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
        if not os.path.exists("./data/secret.txt"):
            with open("./data/secret.txt", "wb") as fp:
                fp.write(os.urandom(32))
        with open("./data/secret.txt", "rb") as fp:
            secret_key = fp.read()
        app.config.from_mapping(
            SECRET_KEY=secret_key,
        )
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    ###################################################################
    # Load database

    m.db.init_app(app)

    @click.command("init-db")
    def init_db_command():  # pragma: no cover
        """Clear the existing data and create new tables."""
        with app.app_context():
            m.db.create_all()
            m.populate_example_data(m.db)
        click.echo("Initialized the database.")

    app.cli.add_command(init_db_command)

    # @app.teardown_request
    # def teardown_db(exception=None) -> None:
    #    if exception:
    #        g.db.rollback()
    #    else:
    #        g.db.commit()
    #    g.db.close()

    ###################################################################
    # Public routes

    app.add_url_rule(
        "/graphql",
        view_func=MyGraphQLView.as_view("graphql_view", schema=s.schema, graphql_ide=True),
    )

    @app.route("/calendar/<path:id>.ics")
    def calendar(id: str) -> Response:
        events = m.db.session.execute(select(m.Event)).scalars()
        import icalendar as c

        cal = c.Calendar()
        cal.add("prodid", "-//Event Index//events.shish.io//")
        cal.add("version", "2.0")
        for event in events:
            cal.add_component(
                c.Event(
                    uid=f"{event.id}@events.shish.io",
                    dtstamp=c.vDatetime(datetime.datetime.now()),
                    created=c.vDatetime(event.created),
                    last_modified=c.vDatetime(event.last_updated),
                    summary=event.title,
                    description=event.description,
                    dtstart=c.vDatetime(event.start_time),
                    dtend=c.vDatetime(event.end_time),
                    # sequence=0,
                    # status='CONFIRMED',
                    # transparency='OPAQUE',
                    # location='Somewhere',
                    # organizer='mailto:" + event.owner.email,"
                    # url='http://example.com',
                    # categories=['Event'],
                    # class='PUBLIC',
                    # geo=(37.386013, -122.082932),
                    # priority=5,
                    # resources=['Easels'],
                    # comment='This is a comment',
                    # alarms=[{'action': 'DISPLAY', 'trigger': '-PT1H'}],
                    # rrule={'freq': 'DAILY', 'count': 10}
                )
            )
        data = cal.to_ical()
        return Response(data, mimetype="text/calendar")

    @app.route("/favicon.svg")
    def favicon() -> Response:
        if os.path.exists("../frontend/dist/"):
            return app.send_static_file("favicon.svg")
        else:
            return Response(
                "Frontend has not been built", mimetype="image/svg+xml; charset=utf-8"
            )

    @app.route("/heartbeat")
    def heartbeat():
        return jsonify({"status": "healthy"})

    @app.route("/assets/<path:x>")
    def assets(x: str) -> str:
        return app.send_static_file(f"assets/{x}")

    @app.route("/error")
    def error():
        raise Exception("This is a test exception")

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def root(path) -> Response:
        if os.path.exists("../frontend/dist/"):
            return app.send_static_file("index.html")
        else:
            return Response("Frontend has not been built", mimetype="text/html")

    return app
