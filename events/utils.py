import functools

from flask import Response, g, redirect, session, url_for
from flask_htmx import HTMX, make_response

from . import models as m
from .app import app
from .models import db

htmx = HTMX()


def hx_err(code: int, msg: str) -> Response:
    return make_response(msg, code, retarget="#toast")


def hx_redirect(location: str) -> Response:
    return make_response(location=location)


@app.before_request
def load_logged_in_user():
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        g.user = db.get_or_404(m.User, user_id)

    if g.user:
        persona_id = session.get("persona_id")
        if persona_id is None:
            g.persona = g.user.default_persona
        else:
            for persona in g.user.personas:
                if persona.id == persona_id:
                    g.persona = persona
                    break
    else:
        g.persona = None


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            if htmx:
                return hx_err(401, "You must be logged in to access this page")
            else:
                return redirect(url_for("index"))
        return view(**kwargs)

    return wrapped_view
