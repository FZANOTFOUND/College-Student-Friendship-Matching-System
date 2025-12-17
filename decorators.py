from functools import wraps
from flask import make_response, render_template, render_template_string
from flask_jwt_extended import verify_jwt_in_request


def jwt_required_or_redirect():
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                print(222)
                verify_jwt_in_request()
            except Exception:
                print(111)
                return make_response(render_template("redirect_on_401.html"), 401)

            return fn(*args, **kwargs)

        return wrapper

    return decorator
