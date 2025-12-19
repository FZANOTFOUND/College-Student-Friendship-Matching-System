from flask import Blueprint

api_tags_bp = Blueprint('api_tags', __name__)
tags_bp = Blueprint('tags', __name__)

from . import api
from . import views