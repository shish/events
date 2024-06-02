import os
from flask import Response, send_from_directory, render_template, request, redirect, url_for, session, g, abort
from sqlalchemy import select
import datetime

from .app import app
from .models import db
from . import models as m
from .utils import *


###################################################################
# Root

@app.route("/favicon.ico")
def favicon() -> Response:
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )

@app.route("/")
def index() -> str:
    events = db.session.execute(
        select(m.Event)
        #.where(Event.end_time > func.now())
        .order_by(m.Event.start_time)
        .limit(100)
    ).scalars()
    return render_template(
        "index.html",
        title="Event Index",
        heading="Event Index",
        user=g.user,
        events=events,
    )


###################################################################
# Users

@app.route("/user", methods=["POST"])
def user_create():
    username = request.form["username"]
    if not username:
        return hx_err(403, "Username is required")
    if len(username) >= 32:
        return hx_err(403, "Username needs to be less than 32 characters")
    if username[0] in ("_", "@", "."):
        return hx_err(403, "Username cannot start with _, @, or .")

    user = db.session.execute(
        select(m.User).where(db.func.lower(m.User.username) == db.func.lower(username))
    ).scalar()
    persona = db.session.execute(
        select(m.Persona).where(db.func.lower(m.Persona.name) == db.func.lower(username))
    ).scalar()
    if user or persona:
        return hx_err(403, "That username has already been taken, sorry D:")

    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if not password1:
        return hx_err(403, "Password is required")
    if password1 != password2:
        return hx_err(403, "The password and confirmation password don't match D:")

    email = request.form.get("email", "")

    user = m.User(username, password1, email)
    db.session.add(user)
    db.session.commit()

    session["user_id"] = user.id
    app.logger.info("User created")
    return hx_redirect(url_for("user_read", username=username))

@app.route("/user/<username>", methods=["GET"])
@login_required
def user_read(username: str):
    display_user = db.session.execute(
        select(m.User)
        .where(db.func.lower(m.User.username) == db.func.lower(username))
    ).scalar()
    if not display_user:
        return hx_err(404, "User not found")

    return render_template(
        "user.html",
        display_user=display_user,
        user=g.user,
    )

@app.route("/user/<username>", methods=["POST"])
@login_required
def user_update(username: str):
    if g.user.username != username:
        return hx_err(403, "You can only update your own user information")

    g.user.message = request.form["message"]
    g.user.email = request.form["email"]
    db.session.commit()

    if htmx:
        return render_template("parts/settings.html", user=g.user)
    else:
        return redirect(url_for("user_read", username=username))


###################################################################
# Sessions

@app.route("/session", methods=["POST"])
def session_create():
    username = request.form["username"]
    password = request.form["password"]

    maybe_user = db.session.execute(
        select(m.User)
        .where(db.func.lower(m.User.username) == db.func.lower(username))
    ).scalars().first()
    if maybe_user and maybe_user.check_password(password):
        g.user = maybe_user
        session["user_id"] = g.user.id
        app.logger.info(f"logged in from {request.remote_addr}")
        return hx_redirect(url_for("user_read", username=username))
    else:
        app.logger.info(f"login failed from {request.remote_addr}")
        return hx_err("Invalid username or password")

@app.route("/session", methods=["DELETE"])
def session_delete():
    app.logger.info("logged out")
    session.clear()
    return hx_redirect(url_for("index"))


###################################################################
# Events

@app.route("/event", methods=["POST"])
@login_required
def event_create():
    e = m.Event(
        title=request.form["title"],
        description=request.form["description"],
        start_time=request.form["start_time"],
        end_time=request.form["end_time"],
        owner=g.persona,
    )
    db.session.add(e)
    db.session.commit()
    app.logger.info(f"Event {e.id} created ({e.title})")
    return hx_redirect(url_for("event_read", id=e.id))

@app.route("/event/<id>", methods=["GET"])
def event_read(id: str):
    event = db.session.execute(
        select(m.Event)
        .where(m.Event.id == int(id))
    ).scalar()
    if not event:
        return hx_err(404, "Event not found")
    return render_template(
        "event.html",
        event=event,
        user=g.user,
    )

@app.route("/event/<id>", methods=["POST"])
@login_required
def event_update(id: str):
    e = db.session.execute(
        select(m.Event)
        .where(m.Event.id == int(id))
    ).scalar()
    if not e:
        return hx_err(404, "Event not found")
    if e.owner not in g.user.personas:
        return hx_err(403, "You can only update your own events")
    
    e.title = request.form["title"]
    e.description = request.form["description"]
    e.start_time = request.form["start_time"]
    e.end_time = request.form["end_time"]

    db.session.commit()
    app.logger.info(f"Event {e.id} updated")
    if htmx:
        return render_template("parts/event.html", event=e)
    else:
        return hx_redirect(url_for("event_read", id=id))

@app.route("/event/<id>", methods=["DELETE"])
@login_required
def event_delete(id: str):
    event = db.session.execute(
        select(m.Event)
        .where(m.Event.id == int(id))
        .where(m.Event.owner_id == g.user.id)
    ).scalar()
    if event:
        db.session.delete(event)
        db.session.commit()
    app.logger.info(f"Event {id} removed")
    return hx_redirect(url_for("index"))


###################################################################
# Calendar

@app.route("/calendar/<path:id>.ics")
def calendar(id: str) -> Response:
    events = db.session.execute(select(m.Event)).scalars()
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