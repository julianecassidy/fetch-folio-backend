"""Models for FetchFolio app."""
 
import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields
from datetime import datetime, timedelta
from flask_bcrypt import Bcrypt
import jwt

bcrypt = Bcrypt()
db = SQLAlchemy()
ma = Marshmallow()

SECRET_KEY = os.environ['SECRET_KEY']

def connect_db(app):
    """Connect to database."""

    app.app_context().push()
    db.app = app
    db.init_app(app)

DEFAULT_IMAGE_URL = "https://paradepets.com/.image/c_limit%2Ccs_srgb%2Cq_auto:good%2Cw_760/MTkxMzY1Nzg4MTM2NzExNzc4/teacup-dogs-jpg.webp"


class CommandNote(db.Model):
    """CommandNote class."""

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

    # command = relationship from note to a command


class CommandNoteSchema(ma.SQLAlchemyAutoSchema):
    """CommandNote schema."""

    class Meta():
        model = CommandNote
        fields = ("id", "note", "date")


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

    date_updated = db.Column(
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
        db.ForeignKey('commands_types.type'),
        nullable=False,
    )

    dog_id = db.Column(
        db.Integer,
        db.ForeignKey('dogs.id'),
        nullable=False,
    )

    notes = db.relationship("CommandNote", backref="command")

    # dog = relationship from command to the dog


class CommandSchema(ma.SQLAlchemyAutoSchema):
    """Command schema."""

    class Meta():
        model = Command
        fields = (
            "id", 
            "name", 
            "date_introduced", 
            "date_updated", 
            "description",
            "voice_command",
            "video_command",
            "command_video_url",
            "proficiency",
            "performance_vdieo_url",
            "notes",
            )
        
    notes = fields.Nested(
        "CommandNoteSchema", 
        only=("id", "note", "date"), 
        many=True
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
        default=datetime.utcnow() + timedelta(hours=1),
    )

    location = db.Column(
        db.String(100),
        nullable=False,
        default='',
    )

    dog_id = db.Column(
        db.Integer,
        db.ForeignKey('dogs.id'),
        nullable=False,
    )

    type = db.Column(
        db.String(30),
        db.ForeignKey('events_types.type'),
        nullable=False,
    )

    # dog = relationship from an event to the dog


class EventSchema(ma.SQLAlchemyAutoSchema):
    """Event schema."""

    model = Event
    fields = ("id", "title", "start_time", "end_time", "location", "dog_id", "type")


class EventType(db.Model):
    """EventType class."""

    __tablename__ = "events_types"

    type = db.Column(
        db.String(30),
        primary_key=True,
    )


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

    private = db.Column(
        db.Boolean,
        nullable=False,
        default=True,
    )

    owner_username = db.Column(
        db.String(50),
        db.ForeignKey('users.username'),
        nullable=False,
    )

    commands = db.relationship("Command", backref="dog")

    events = db.relationship("Event", backref="dog")

    # owner = relationship from a dog to it's owner(user)

    def serialize(self):
        """Make a dictionary of current dog instance."""

        dog = {
            "id": self.id,
            "name": self.name,
            "birth_date": self.birth_date,
            "breed": self.breed,
            "size": self.size,
            "bio": self.bio,
            "image_url": self.image_url,
            "private": self.private,
            "owner_username": self.owner_username,
        }
        
        return dog
    
    
class DogSchema(ma.SQLAlchemyAutoSchema):
    """Dog schema."""

    class Meta:
        model = Dog
        fields = (
            "id", 
            "name", 
            "birth_date", 
            "breed", 
            "size", 
            "bio", 
            "image_url",
            "private",
            "owner_username",
            "commands",
            "events",
        )

    commands = fields.Nested(
        "CommandSchema", 
        only=("id", "name", "voice_command", "proficiency", "type", "date_updated"),
        many=True
    )

    events = fields.Nested(
        "EventSchema",
        only=("id", "title" "start_time", "location", "type"),
        many=True
    )
    

class User(db.Model):
    """User class."""

    __tablename__ = 'users'

    username = db.Column(
        db.String(50),
        primary_key=True,
    )

    password = db.Column(
        db.Text,
        nullable=False,
    )

    email = db.Column(
        db.String(50),
        nullable=False,
    )

    name = db.Column(
        db.String(50),
        nullable=False,
    )

    bio = db.Column(
        db.Text,
    )

    location = db.Column(
        db.Text,
    )

    dogs = db.relationship("Dog", backref='owner')

    @classmethod
    def signup(cls, username, password, name, email):
        """Sign up user. Hashes password and adds user to database."""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            password=hashed_pwd,
            name=name,
            email=email,
        )

        db.session.add(user)
        return user
    
    @classmethod
    def login(cls, username, password):
        """Log in user. Find user with "username" and "password" and return that
        user.
        
        If there is no matching username or the password is wrong, return false."""

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user.username
        
        return False

    @classmethod
    def create_token(cls, username):
        """Create a JWT for user and return."""

        return jwt.encode({"username": username}, SECRET_KEY, algorithm="HS256")

    def serialize(self):
        """Make a dictionary of current user instance."""

        user = {
            "username": self.username,
            "name": self.name,
            "email": self.email,
            "bio": self.bio,
            "location": self.location,
            }
        
        return user
    

class UserSchema(ma.SQLAlchemyAutoSchema):
    """User schema."""

    class Meta:
        model = User
        fields = ("id", "username", "name", "email", "bio", "location", "dogs")
        
    dogs = fields.Nested("DogSchema", only=("id",), many=True)