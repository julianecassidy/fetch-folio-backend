import os
from flask import request, g
from functools import wraps
from werkzeug.exceptions import Unauthorized

def require_user(f):
    """Check request has a valid JWT for logged in user."""

    @wraps(f)
    def decorated(*args, **kwargs):
        print("REQUIRE_USER DECORATOR")
        
        if g.user:
            return f(*args, **kwargs)
        
        else:
            raise Unauthorized()
    
    return decorated