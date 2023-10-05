"""Flask app for FetchFolio app."""

import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request, g
from flask_cors import CORS
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
from werkzeug.exceptions import BadRequest, Unauthorized
import jwt
import logging
import uuid


from models import db, connect_db, User, Dog, Command, CommandNote, CommandTemplate, Event
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
            current_username = User.query.get(data["username"])
            if current_username is None:
                raise Unauthorized("Invalid token.")
            else:
                g.user = current_username
                print("\033[96m"+ 'PRINT >>>>> ' + "\033[00m", "g", g.user)
            
        except Exception as e:
            g.user = None
    
    else:
        g.user = None    
    

@app.post('/signup')
def signup():
    """Handle user signup.

    Take inputted JSON user data and create new user in DB. Return JWT.
    If errors, throw BadRequest Error.
    """

    try:
        User.signup(
            username=request.json["username"],
            password=request.json["password"],
            name=request.json["name"],
            email=request.json["email"],
        )

        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        raise BadRequest("Username already in use. No user created.")

    token = User.create_token(request.json["username"])
    return jsonify(token)


@app.post('/login')
def login():
    """Handle user login.

    Taken JSON email/username and password. Return JWT if valid user.
    If invalid, throw Unauthorized Error."""

    username = User.login(
        username=request.json["username"],
        password=request.json["password"]
    )

    print("\033[96m"+ 'PRINT >>>>> ' + "\033[00m", "USER", username)

    if username:
        token = User.create_token(username)
        return jsonify(token)
    
    else:
        raise Unauthorized("Username/password invalid.")
    

#################################################################### User Routes

@app.get('/users/<username>')
@require_user
def get_user(username):
    """Get user from database. Must be logged in."""

    user_instance = User.query.get_or_404(username)
    user = user_instance.serialize()
    return jsonify(user)

@app.patch('/users/<username>')
@require_user
def update_user_profile(username):
    """Update a user's information. Must be logged in as same user in params."""

    if username != g.user.username:
        raise Unauthorized
    
    user = User.query.get_or_404(username)

    try:
        user.name = request.json["name"]
        user.email = request.json["email"],
        user.location = request.json["location"],
        user.bio = request.json["bio"],

        db.session.commit()
    
    except:
        db.session.rollback()
        raise BadRequest

    updated_user_instance = User.query.get(username)
    updated_user = updated_user_instance.serialize()
    return jsonify(updated_user)
    
@app.delete('/users/<username>')
@require_user
def delete_user(username):
    """Delete a user's account. Must be logged in as same user in params."""

    if username != g.user.username:
        raise Unauthorized
    
    ## TODO: need to delete dogs, commands, command notes, events

    # return f"{username} deleted"
    return "this method is coming soon"


##################################################################### Dog Routes

@app.get('/dogs')
@require_user
def get_dogs():
    """Get all dogs in databse not marked private. Must be logged in."""

    dogs_instances = Dog.query.filter_by(private=False).all()


@app.get('/<username>/dogs')
@require_user
def get_users_dogs(username):
    """Get all dogs for a user. Must be logged in as same user in params."""


@app.get('/<username>/dog/<dog>')
@require_user
def get_users_dog(username, dog):
    """Get dog. Must be logged in as same user in params."""