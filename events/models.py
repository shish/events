import datetime
import bcrypt
import typing as t

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
SECURE = True


user_personas = db.Table(
    "user_personas",
    Base.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("persona_id", ForeignKey("persona.id"), primary_key=True),
)

class Persona(db.Model):  # type: ignore
    __tablename__ = "persona"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    created: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)
    last_updated: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    users: Mapped[t.List["User"]] = relationship(
        secondary=user_personas, back_populates="personas"
    )

class User(db.Model):  # type: ignore
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(nullable=False, index=True)
    message: Mapped[str] = mapped_column(default="")
    password: Mapped[str]
    email: Mapped[str]
    created: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)
    last_updated: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now, onupdate=datetime.datetime.now
    )

    personas: Mapped[t.List[Persona]] = relationship(
        secondary=user_personas, back_populates="users"
    )

    def __init__(self, username: str, password: str, email: str) -> None:
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

    def __repr__(self) -> str:
        return f"User({self.username!r})"
    
    @property
    def default_persona(self) -> Persona:
        for persona in self.personas:
            if persona.name == self.username:
                return persona
        return self.personas[0]


event_tags = db.Table(
    "event_tags",
    Base.metadata,
    Column("event_id", ForeignKey("event.id"), primary_key=True),
    Column("tag_id", ForeignKey("tag.id"), primary_key=True),
)


class Event(db.Model):
    __tablename__ = "event"

    id: Mapped[int] = mapped_column("id", primary_key=True)
    title: Mapped[str]
    description: Mapped[str]
    owner_id: Mapped[int] = mapped_column(ForeignKey(Persona.id), index=True)
    created: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)
    last_updated: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
    start_time: Mapped[datetime.datetime]
    end_time: Mapped[datetime.datetime]

    tags: Mapped[t.List["Tag"]] = relationship(
        secondary=event_tags, back_populates="events"
    )
    owner: Mapped[Persona] = relationship("Persona")


class Tag(db.Model):
    __tablename__ = "tag"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    events: Mapped[t.List[Event]] = relationship(
        secondary=event_tags, back_populates="tags"
    )

    def __init__(self, name: str) -> None:
        self.name = name
