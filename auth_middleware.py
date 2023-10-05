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
            print("\033[96m"+ 'PRINT >>>>> ' + "\033[00m", "yes g user")
            return f(*args, **kwargs)
        
        else:
            print("\033[96m"+ 'PRINT >>>>> ' + "\033[00m", "no g user")

            raise Unauthorized()
    
    return decorated