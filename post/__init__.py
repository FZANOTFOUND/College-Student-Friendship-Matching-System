from flask import Blueprint

api_post_bp = Blueprint('api_post', __name__)
post_bp = Blueprint('post', __name__)
from . import api
from . import views

