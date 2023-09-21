"""Models for FetchFolio app."""
 
from datetime import datetime, timedelta
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    """Connect to database."""

    app.app_context().push()
    db.app = app
    db.init_app(app)

DEFAULT_IMAGE_URL = "https://paradepets.com/.image/c_limit%2Ccs_srgb%2Cq_auto:good%2Cw_760/MTkxMzY1Nzg4MTM2NzExNzc4/teacup-dogs-jpg.webp"


class Dog(db.Model):
    """Dog class."""

    __tablename__ = 'dogs'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.String(100),
        nullable=False,
    )

    birth_date = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    breed = db.Column(
        db.String,
        nullable=False,
    )

    size = db.Column(
        db.String(10),
        nullable=False,
    )

    bio = db.Column(
        db.Text,
        nullable=False,
        default='',
    )

    image_url = db.Column(
        db.Text,
        nullable=False,
        default=DEFAULT_IMAGE_URL,
    )

    owner_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False,
    )


class User(db.Model):
    """User class."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True,
    )

    bio = db.Column(
        db.Text,
    )

    location = db.Column(
        db.Text,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )


class Command(db.Model):
    """Command class."""

    __tablename__ = 'commands'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.String(200),
        nullable=False,
    )

    date_introduced = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    description = db.Column(
        db.Text,
        nullable=False,
        default='',
    )

    voice_command = db.Column(
        db.String(100),
        nullable=False,
        default='',
    )

    visual_command = db.Column(
        db.String(100),
        nullable=False,
        default='',
    )

    command_video_url = db.Column(
        db.Text,
        nullable=False,
        default='',
    )

    proficiency = db.Column(
        db.Integer,
        nullable=False,
        default=1,
    )

    performance_video_url = db.Column(
        db.Text,
        nullable=False,
        default='',
    )

    type = db.Column(
        db.String(10),
        db.ForeignKey('command_types.type'),
        nullable=False,
    )

    dog = db.Column(
        db.Integer,
        db.ForeignKey('dogs.id'),
        nullable=False,
    )


class CommandNote(db.Model):
    """CommandModel class."""

    __tablename__ = 'commands_notes'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    note = db.Column(
        db.Text,
        nullable=False,
        default='',
    )

    date = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    command_id = db.Column(
        db.Integer,
        db.ForeignKey('commands.id'),
        nullable=False,
    )


class CommandTemplate(db.Model):
    """CommandTemplate class."""

    __tablename__ = 'commands_templates'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.String(200),
        nullable=False,
    )

    description = db.Column(
        db.Text,
        nullable=False,
        default='',
    )

    voice_command = db.Column(
        db.String(100),
        nullable=False,
        default='',
    )

    visual_command = db.Column(
        db.String(100),
        nullable=False,
        default='',
    )

    command_video_url = db.Column(
        db.Text,
        nullable=False,
        default='',
    )

    proficiency = db.Column(
        db.Integer,
        nullable=False,
        default=1,
    )

    type = db.Column(
        db.String(10),
        db.ForeignKey('commands_types.type'),
        nullable=False,
    )
    

class CommandType(db.Model):
    """CommandType class for constraint."""

    __tablename__ = 'commands_types'

    type = db.Column(
        db.String(30),
        primary_key=True,
    )


class Event(db.Model):
    """Event class."""

    __tablename__ = "events"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    title = db.Column(
        db.String(200),
        nullable=False,
    )

    start_time = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    end_time = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow + timedelta(hours=1),
    )

    dog = db.Column(
        db.Integer,
        db.ForeignKey('dogs.id'),
        nullable=False,
    )

    type = db.Column(
        db.String(30),
        db.ForeginKey('events_types.type'),
        nullable=False,
    )


class EventType(db.Model):
    """EventType class."""

    __tablename__ = "events_types"

    type = db.Column(
        db.String(30),
        primary_key=True,
    )