# mypy: disable-error-code="misc"

import typing as t
import re
import datetime
from typing import TypedDict
from flask.sessions import SessionMixin

from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import Session
import strawberry
from strawberry_sqlalchemy_mapper import StrawberrySQLAlchemyMapper, StrawberrySQLAlchemyLoader  # type: ignore
from strawberry.permission import BasePermission
from strawberry.types.info import Info as SInfo

from . import models as m
from .query_counter import QueryCounter

strawberry_sqlalchemy_mapper: StrawberrySQLAlchemyMapper = StrawberrySQLAlchemyMapper()


Context = TypedDict(
    "Context",
    {
        "db": Session,
        "cookie": SessionMixin,
        "sqlalchemy_loader": StrawberrySQLAlchemyLoader,
        "cache": t.Dict[str, t.Any],
    },
)
Info = SInfo[Context, None]


#############################################
# Database Types
#############################################

# Users


class UserOnlyViewOwnUserDetails(BasePermission):
    message = "You can only view your own data."

    def has_permission(self, source: m.User, info: Info, **kwargs) -> bool:
        return source.username == info.context["cookie"].get("username")


@strawberry_sqlalchemy_mapper.type(m.User)
class User:
    __exclude__ = ["id", "email", "password"]

    @strawberry.field(permission_classes=[UserOnlyViewOwnUserDetails])
    def email(self: m.User, info: Info) -> str:
        return self.email

    @strawberry.field(
        permission_classes=[UserOnlyViewOwnUserDetails], graphql_type=t.List["User"]
    )
    def friends(self: m.User, info: Info) -> t.List[m.User]:
        return list(self.friends)

    @strawberry.field(
        permission_classes=[UserOnlyViewOwnUserDetails], graphql_type=t.List["User"]
    )
    def friends_outgoing(self: m.User, info: Info) -> t.List[m.User]:
        return [f.friend_b for f in self.friends_outgoing if not f.confirmed]

    @strawberry.field(
        permission_classes=[UserOnlyViewOwnUserDetails], graphql_type=t.List["User"]
    )
    def friends_incoming(self: m.User, info: Info) -> t.List[m.User]:
        return [f.friend_a for f in self.friends_incoming if not f.confirmed]

    @strawberry.field
    def is_friend(self: m.User, info: Info) -> bool:
        return self in get_me_or_die(info, "Anonymous has no friends").friends


# Events


@strawberry_sqlalchemy_mapper.type(m.Event)
class Event:
    __exclude__ = ["user_id"]

    @strawberry.field
    def tags(self: m.Event, info: Info) -> t.List[str]:
        return [tag.name for tag in self.tags]


@strawberry.input
class EventInput:
    title: t.Optional[str] = None
    description: str
    tags: t.Optional[t.List[str]] = None
    startTime: t.Optional[datetime.datetime] = None
    endTime: t.Optional[datetime.datetime] = None


#############################################
# Functions
#############################################


@strawberry.type
class Query:
    @strawberry.field(graphql_type=t.Optional[User])
    def user(self, info: Info, username: t.Optional[str] = None) -> t.Optional[m.User]:
        me = get_me(info)
        if username:
            if not me:
                raise Exception("Anonymous users can't view other users")
            else:
                return by_username(info, username)
        else:
            return me

    @strawberry.field(graphql_type=t.Sequence[Event])
    def events(self, info: Info) -> t.Sequence[m.Event]:
        db = info.context["db"]
        return db.query(m.Event).all()

    @strawberry.field(graphql_type=Event)
    def event(self, info: Info, event_id: int) -> m.Event:
        db = info.context["db"]
        return db.query(m.Event).where(m.Event.id == event_id).one()


@strawberry.type
class Mutation:
    ###################################################################
    # Sessions
    @strawberry.mutation(graphql_type=t.Optional[User])
    def create_user(
        self, info: Info, username: str, password1: str, password2: str, email: str
    ) -> t.Optional[m.User]:
        db = info.context["db"]
        user = by_username(info, username)
        if user:
            if user.check_password(password1):
                info.context["cookie"]["username"] = user.username
                return user
            raise Exception("A user with that name already exists")

        validate_new_username(info, username)
        validate_new_password(password1, password2)
        user = m.User(username, password1, email)
        db.add(user)
        db.flush()
        info.context["cookie"]["username"] = user.username
        return user

    @strawberry.mutation(graphql_type=User)
    def update_user(
        self,
        info: Info,
        password: str,
        username: str,
        password1: str,
        password2: str,
        email: str,
    ) -> m.User:
        db = info.context["db"]
        user = get_me_or_die(info, "Anonymous users can't save settings")

        if not user.check_password(password):
            raise Exception("Current password incorrect")

        if username and username != user.username:
            validate_new_username(info, username)
            user.username = username
            info.context["cookie"]["username"] = user.username
        if password1:
            validate_new_password(password1, password2)
            user.set_password(password1)
        if email:
            user.email = email
        db.flush()
        return user

    @strawberry.mutation(graphql_type=t.Optional[User])
    def login(self, info: Info, username: str, password: str) -> t.Optional[m.User]:
        user = by_username(info, username)
        if not user or not user.check_password(password):
            raise Exception("User not found")
        info.context["cookie"].permanent = True
        info.context["cookie"]["username"] = user.username
        return user

    @strawberry.mutation
    def logout(self, info: Info) -> None:
        if "username" in info.context["cookie"]:
            del info.context["cookie"]["username"]

    ###################################################################
    # Friendships
    @strawberry.mutation
    def add_friend(self, info: Info, username: str) -> None:
        db = info.context["db"]
        user = get_me_or_die(info, "Anonymous users can't add friends")
        friend = by_username(info, username)
        if not friend:
            raise Exception("User not found")
        if friend.id == user.id:
            raise Exception("You can't add yourself")
        for friendship in user.friends_incoming:
            if friendship.friend_a_id == friend.id:
                friendship.confirmed = True
                return
        for friendship in user.friends_outgoing:
            if friendship.friend_b_id == friend.id:
                raise Exception("Friend request already sent")

        friendship = m.Friendship(friend_a_id=user.id, friend_b_id=friend.id)
        db.add(friendship)
        db.flush()

    @strawberry.mutation
    def remove_friend(self, info: Info, username: str) -> None:
        db = info.context["db"]
        user = get_me_or_die(info, "Anonymous users can't remove friends")
        friend = by_username(info, username)
        if not friend:
            raise Exception("User not found")
        db.query(m.Friendship).filter(
            or_(
                and_(
                    m.Friendship.friend_a_id == user.id,
                    m.Friendship.friend_b_id == friend.id,
                ),
                and_(
                    m.Friendship.friend_a_id == friend.id,
                    m.Friendship.friend_b_id == user.id,
                ),
            )
        ).delete()
        db.flush()

    ###################################################################
    # Surveys
    @strawberry.mutation(graphql_type=Event)
    def create_event(self, info: Info, event: EventInput) -> m.Event:
        db = info.context["db"]
        user = get_me_or_die(info, "Anonymous users can't create events")

        # make sure the new survey has an ID
        new_event = m.Event(
            title=event.title,
            description=event.description,
            user_id=user.id,
            tags=[get_or_create_tag(info, t) for t in (event.tags or [])],
            last_updated=datetime.datetime.now(),
            start_time=event.startTime,
            end_time=event.endTime,
        )
        db.add(new_event)
        db.flush()

        return new_event


#######################################################################
# Utils


def validate_new_username(info: Info, username: str) -> None:
    if not username:
        raise Exception("Username is required")
    if len(username) >= 32:
        raise Exception("Username needs to be less than 32 characters")
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        raise Exception("Username can only contain letters, numbers, and underscores")
    if existing := by_username(info, username):
        me = get_me(info)
        if not me or existing.id != me.id:
            raise Exception("Another user with that name already exists")


def validate_new_password(password1: str, password2: str) -> None:
    if not password1 or password1 != password2:
        raise Exception("Bad password")


def get_me(info: Info) -> t.Optional[m.User]:
    return by_username(info, info.context["cookie"].get("username"))


def get_me_or_die(info: Info, msg: str) -> m.User:
    user = get_me(info)
    if not user:
        raise Exception(msg)
    return user


def by_username(info: Info, username: t.Optional[str]) -> t.Optional[m.User]:
    if not username:
        return None
    cache = info.context["cache"]
    db = info.context["db"]
    key = f"user-{username}"
    if key not in cache:
        stmt = select(m.User).where(func.lower(m.User.username) == func.lower(username))
        cache[key] = db.execute(stmt).scalars().first()
    return cache[key]


def get_or_create_tag(info: Info, name: str) -> m.Tag:
    db = info.context["db"]
    stmt = select(m.Tag).where(func.lower(m.Tag.name) == func.lower(name))
    t = db.execute(stmt).scalars().first()
    if not t:
        t = m.Tag(name=name)
        db.add(t)
    return t


#######################################################################
# Schema

strawberry_sqlalchemy_mapper.finalize()
schema = strawberry.Schema(query=Query, mutation=Mutation, extensions=[QueryCounter])
