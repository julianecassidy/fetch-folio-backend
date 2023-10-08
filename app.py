"""Flask app for FetchFolio app."""

import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request, g, abort
from flask_cors import CORS
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
from werkzeug.exceptions import BadRequest, Unauthorized
import jwt
import logging
import uuid


from models import (db, connect_db, User, UserSchema, Dog, DogSchema,Command, CommandSchema,
                    CommandNote, CommandNoteSchema, CommandTemplate, Event, EventSchema)
from auth_middleware import require_user

load_dotenv()

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']

connect_db(app)

# logging.getLogger('flask_cors').level = logging.DEBUG

# Having the Debug Toolbar show redirects explicitly is often useful;
# however, if you want to turn it off, you can uncomment this line:
#
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

users_schema = UserSchema()
dogs_schema = DogSchema()
commands_schema = CommandSchema()
commands_notes_schema = CommandNoteSchema()
events_schema = EventSchema()

######################################################  User Signup/Login/Logout

@app.before_request
def add_user_to_g():
    """If there is a user logged in, add the current user to Flask global."""

    token = None
    if "Authorization" in request.headers:
        token = request.headers["Authorization"]

    if token:
        try:
            data = jwt.decode(token, os.environ['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(data["username"])
            if current_user is None:
                raise Unauthorized("Invalid token.")
            else:
                g.user = current_user
                print("\033[96m"+ 'PRINT >>>>> ' + "\033[00m", "g", g.user)
            
        except Exception as e:
            g.user = None
    
    else:
        g.user = None    
    

@app.post('/signup')
def signup():
    """Handle user signup. Take inputted JSON user data and create new user in DB.
      Requires:
      {
        "username": "jules",
        "email": "julianecassidy@gmail.com",
        "password": "password",
        "name": "Jules"
        "user_image_url": file // optional
      }

    Return JWT string. If errors, throw BadRequest Error.
    """

    try:
        User.signup(
            username=request.json["username"],
            password=request.json["password"],
            name=request.json["name"],
            email=request.json["email"],
            user_image_url=request.json.get("user_image_url"),
        )

        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        raise BadRequest("Username already in use. No user created.")

    token = User.create_token(request.json["username"])
    return jsonify(token)


@app.post('/login')
def login():
    """Handle user login. Take JSON email/username and password:
    {"username": "jules",
    "password": "password"}
    
    Return JWT string if valid user. If invalid, throw Unauthorized Error."""

    user = User.login(
        username=request.json["username"],
        password=request.json["password"]
    )

    if user:
        token = User.create_token(user.username)
        return jsonify(token)
    
    else:
        raise Unauthorized("Username/password invalid.")
    

#################################################################### User Routes

@app.get('/users')
@require_user
def get_users():
    """Get all users. Returns:
    [
        {
            "bio": null,
            "dogs": [],
            "email": "julianecassidy@gmail.com",
            "location": null,
            "name": "Jules",
            "username": "jules"
            "user_image_url": "https://image.com"
        }, ...
    ]

    Must be logged in.
    """

    users_instances = User.query.all()
    users = [user_instance.serialize() for user_instance in users_instances]

    return jsonify(users)

@app.get('/users/current')
@require_user
def get_user():
    """Get user. Returns:
        {
        "bio": null,
        "dogs": [],
        "email": "julianecassidy@gmail.com",
        "location": null,
        "name": "Jules",
        "username": "jules"
        "user_image_url": "https://image.com"
        }

    Must be logged in."""

    user_instance = g.user
    user = users_schema.dump(user_instance)
    return jsonify(user)

@app.patch('/users/current')
@require_user
def update_user_profile():
    """Update a user's information. Can take:
    {
        "name": "Jules",
        "email": "julianecassidy@gmail.com",
        "location": "Denver",
        "bio": "good human",
        "user_image_url": "https://image.com"
    }

    Returns:
    {
        "bio": "good human",
        "dogs": [],
        "email": "julianecassidy@gmail.com",
        "location": "Denver",
        "name": "Jules",
        "user_image_url": "https://image.com",
        "username": "jules"
    }

    Must be logged in as same user in params."""
    
    user = g.user
    
    try:
        user.name = request.json.get("name", user.name)
        user.email = request.json.get("email", user.email),
        user.location = request.json.get("location", user.location),
        user.bio = request.json.get("bio", user.bio),
        user.user_image_url = request.json.get("user_image_url", user.user_image_url)

        db.session.commit()
    
    except:
        db.session.rollback()
        raise BadRequest

    updated_user_instance = User.query.get(user.username)
    updated_user = users_schema.dump(updated_user_instance)
    return jsonify(updated_user)

@app.put('/users/current')
@require_user
def update_password(username):
    """Updates a user's password. Requires:
    {old_password, new_passwword}
    
    Must be logged in as same user in params."""
   
    user = g.user

    try:
        user.update_password
        db.session.commit()

    except Unauthorized:
        db.session.rollback()
        raise Unauthorized("Password incorrect")
    
    except:
        db.session.rollback()
        raise BadRequest

   
@app.delete('/users/current')
@require_user
def delete_user(username):
    """Delete a user's account. Must be logged in."""

    user = g.user
    
    ## TODO: need to delete dogs, commands, command notes, events

    # return f"{username} deleted"
    return "this method is coming soon"


##################################################################### Dog Routes

@app.get('/dogs')
@require_user
def get_dogs():
    """Get all dogs in databse not marked private. Returns:
    [
        {
            "bio": "good dog",
            "birth_date": "Mon, 03 Aug 2020 00:00:00 GMT",
            "breed": "Border Collie",
            "id": 1,
            "image_url": "https://paradepets.com/.image/c_limit%2Ccs_srgb%2Cq_auto:good%2Cw_760/MTkxMzY1Nzg4MTM2NzExNzc4/teacup-dogs-jpg.webp",
            "name": "Petey",
            "owner_username": "jules",
            "private": false,
            "size": "large"
        },...
    ]
    
    Must be logged in."""

    dogs_instances = Dog.query.filter_by(private=False).all()
    dogs = [dog_instance.serialize() for dog_instance in dogs_instances]

    return jsonify(dogs)

@app.get('/dogs/current')
@require_user
def get_users_dogs():
    """Get all dogs for current user. Returns:
    [
        {
            "bio": "good dog",
            "birth_date": "Mon, 03 Aug 2020 00:00:00 GMT",
            "breed": "Border Collie",
            "id": 1,
            "image_url": "https://paradepets.com/.image/c_limit%2Ccs_srgb%2Cq_auto:good%2Cw_760/MTkxMzY1Nzg4MTM2NzExNzc4/teacup-dogs-jpg.webp",
            "name": "Petey",
            "owner_username": "jules",
            "private": false,
            "size": "large"
        },...
    ]
    
    Must be logged in."""

    username = g.user.username
    
    dogs_instances = Dog.query.filter_by(owner_username=username).all()
    dogs = [dog_instance.serialize() for dog_instance in dogs_instances]

    return jsonify(dogs)

@app.get('/dogs/current/<int:dog_id>')
@require_user
def get_users_dog(dog_id):
    """Get dog. Returns:
    {
        "bio": "good dog",
        "birth_date": "2020-08-03T00:00:00",
        "breed": "Border Collie",
        "commands": [],
        "events": [],
        "id": 1,
        "image_url": "https://paradepets.com/.image/c_limit%2Ccs_srgb%2Cq_auto:good%2Cw_760/MTkxMzY1Nzg4MTM2NzExNzc4/teacup-dogs-jpg.webp",
        "name": "Petey",
        "owner_username": "jules",
        "private": false,
        "size": "large"
    }

    Must be logged in as same user in params."""
   
    dog_instance = Dog.query.get_or_404(dog_id)
    dog = dogs_schema.dump(dog_instance)

    return jsonify(dog)

@app.post('/dogs/current')
@require_user
def add_dog():
    """Add dog. Requires:
    {
        "name": "Petey",
        "birth_date": "2020-08-03T00:00:00",
        "breed": "Border Collie",
        "size": "large",
        "bio": "good dog"   // optional
        "private": "false"   // optional, defaults to false
        "image_url": "http://image.com   // optional
    }

    Returns:
    {
        "bio": "good dog",
        "birth_date": "2020-08-03T00:00:00",
        "breed": "Border Collie",
        "commands": [],
        "events": [],
        "id": 1,
        "image_url": "https://paradepets.com/.image/c_limit%2Ccs_srgb%2Cq_auto:good%2Cw_760/MTkxMzY1Nzg4MTM2NzExNzc4/teacup-dogs-jpg.webp",
        "name": "Petey",
        "owner_username": "jules",
        "private": false,
        "size": "large"
    }
    
    Must be logged in as same user in params."""

    username = g.user.username

    try:
        new_dog = Dog(
            name=request.json["name"],
            birth_date=request.json.get("birth_date"),
            breed=request.json["breed"],
            size=request.json["size"],
            bio=request.json.get("bio"),
            image_url=request.json.get("image_url"),
            private=request.json["private"] == "true",
            owner_username=username
        )

        db.session.add(new_dog)
        db.session.commit()
        dog = dogs_schema.dump(new_dog)
        return jsonify(dog)

    # TODO: I'm not sure this is fully debugged. The error has gone away, but
    # we're still missing a field in the schema so I think we haven't fixed it.
    except Exception as e:
        db.session.rollback()
        # raise BadRequest("Dog not created.")
        print("\033[96m"+ 'PRINT >>>>> ' + "\033[00m", e)
        raise BadRequest
    
@app.patch('/dog/current/<int:dog_id>')
@require_user
def update_dog(dog_id):
    """Update dog. Can take:
    - name
    - birth_date
    - breed
    - size
    - bio
    - image_url
    - private

    Returns:
    {
        "bio": "good dog",
        "birth_date": "2020-08-03T00:00:00",
        "breed": "Border Collie",
        "commands": [],
        "events": [],
        "id": 1,
        "image_url": "https://paradepets.com/.image/c_limit%2Ccs_srgb%2Cq_auto:good%2Cw_760/MTkxMzY1Nzg4MTM2NzExNzc4/teacup-dogs-jpg.webp",
        "name": "Petey",
        "owner_username": "jules",
        "private": false,
        "size": "large"
    }
    
    Must be logged in as same user in params."""

    user = g.user
    dog = Dog.query.get(dog_id)

    # dog is not one of logged in user's dogs
    if dog not in user.dogs:
        raise Unauthorized
    
    try:
        dog.name=request.json.get("name"),
        dog.birth_date=request.json.get("birth_date"),
        dog.breed=request.json.get("breed"),
        dog.size=request.json.get("size"),
        dog.bio=request.json.get("bio"),
        dog.image_url=request.json.get("image_url"),
        dog.private=request.json.get("private") == "True",
       
        db.session.commit()
    
    except:
        db.session.rollback()
        raise BadRequest

    updated_dog_instance = Dog.query.get(dog_id)
    updated_dog = dogs_schema.dump(updated_dog_instance)
    return jsonify(updated_dog)

@app.delete('/dogs/current/<int:dog_id>')
@require_user
def delete_dog(dog_id):
    """Remove a dog. Dog has to belong to current user. Returns "dog deleted"."""

    user = g.user
    dog = Dog.query.get(dog_id)

    # dog is not one of logged in user's dogs
    if dog not in user.dogs:
        raise Unauthorized
    
    commands = dog.commands

    try:
        # delete command notes
        [db.session.delete(command.notes) for command in commands]

        # delete commands
        Command.query.filter(Command.dog_id==dog_id).delete()

        # delete events
        Event.query.filter(Event.dog_id==dog_id).delete()

        # delete dog
        db.session.delete(dog)
        db.session.commit()

        return f"{dog.name} deleted"
    
    except:
        raise BadRequest

    
    
