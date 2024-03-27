import typing as t
import bcrypt
import enum
import os
from sqlalchemy import Column, Table, ForeignKey, create_engine, UniqueConstraint, Enum
from sqlalchemy.orm import (
    Session,
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    attribute_keyed_dict,
)

SECURE = True


class Base(DeclarativeBase):
    pass


class Friendship(Base):
    __tablename__ = "friendship"

    friend_a_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"), primary_key=True, index=True
    )
    friend_b_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"), primary_key=True, index=True
    )
    confirmed: Mapped[bool] = mapped_column(default=False)

    friend_a: Mapped["User"] = relationship(
        "User", back_populates="friends_outgoing", foreign_keys=[friend_a_id], lazy="joined"
    )
    friend_b: Mapped["User"] = relationship(
        "User", back_populates="friends_incoming", foreign_keys=[friend_b_id], lazy="joined"
    )


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column("id", primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    password: Mapped[str]
    email: Mapped[str]

    friends_incoming: Mapped[t.List[Friendship]] = relationship(
        "Friendship", foreign_keys=[Friendship.friend_b_id], back_populates="friend_b"
    )
    friends_outgoing: Mapped[t.List[Friendship]] = relationship(
        "Friendship", foreign_keys=[Friendship.friend_a_id], back_populates="friend_a"
    )

    def __init__(self, username: str, password: str, email: str = ""):
        self.username = username
        self.email = email
        self.set_password(password)

    def set_password(self, password: str) -> None:
        given = password.encode()
        if SECURE:  # pragma: no cover
            self.password = bcrypt.hashpw(given, bcrypt.gensalt()).decode()
        else:
            self.password = password

    def check_password(self, password: str) -> bool:
        given = password.encode()
        current = self.password.encode()
        if SECURE:  # pragma: no cover
            return bcrypt.hashpw(given, current) == current
        else:
            return given == current

    @property
    def friends(self) -> t.Iterator["User"]:
        for outgoing in self.friends_outgoing:
            if outgoing.confirmed:
                yield outgoing.friend_b
        for incoming in self.friends_incoming:
            if incoming.confirmed:
                yield incoming.friend_a

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User {self.username}>"


event_tags = Table(
    "event_tags",
    Base.metadata,
    Column("event_id", ForeignKey("event.id"), primary_key=True),
    Column("tag_id", ForeignKey("tag.id"), primary_key=True),
)

class Event(Base):
    __tablename__ = "event"

    id: Mapped[int] = mapped_column("id", primary_key=True)
    title: Mapped[str]
    description: Mapped[str]
    user_id: Mapped[int] = mapped_column("user_id", ForeignKey("user.id"), index=True)
    tags: Mapped[t.List["Tag"]] = relationship(secondary=event_tags, back_populates="events")
    owner: Mapped[User] = relationship("User")


class Tag(Base):
    __tablename__ = "tag"
    id: Mapped[int] = mapped_column("id", primary_key=True)
    name: Mapped[str]
    events: Mapped[t.List[Event]] = relationship(secondary=event_tags, back_populates="tags")


def populate_example_data(db: Session):
    users: t.List[User] = []
    created_users = False
    for name in ["Alice", "Bob", "Charlie", "Dave", "Evette", "Frank"]:
        user = db.query(User).filter(User.username == name).first()
        if not user:
            created_users = True
            user = User(name, name.lower() + "pass")
            users.append(user)
            db.add(user)
    [alice, bob, charlie, dave, evette, frank] = users
    alice.email = "alice@example.com"

    if created_users:
        f = Friendship(friend_a=alice, friend_b=bob, confirmed=True)
        db.add(f)

        f = Friendship(friend_a=charlie, friend_b=alice, confirmed=False)
        db.add(f)

    tags: t.List[Tag] = []
    for name in ["in-person", "online", "social"]:
        tag = db.query(Tag).filter(Tag.name == name).first()
        if not tag:
            tag = Tag(name=name)
            tags.append(tag)
            db.add(tag)
    [in_person, online, social] = tags

    e1 = db.query(Event).filter(Event.title == "Crafty Time").first()
    if not e1:
        e1 = Event(
            title="Crafty Time",
            owner=alice,
            description="Let's meet up and make some stuff",
            tags=[online, social]
        )
        db.add(e1)
        db.flush()

    e2 = db.query(Event).filter(Event.title == "Karaoke").first()
    if not e2:
        e2 = Event(
            title="Karaoke",
            owner=alice,
            description="Singalingalong",
            tags=[in_person, social]
        )
        db.add(e2)
        db.flush()

    db.commit()


if __name__ == "__main__":  # pragma: no cover
    os.makedirs("./data", exist_ok=True)
    engine = create_engine("sqlite:///data/events.sqlite", echo=False)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    populate_example_data(Session(engine))
