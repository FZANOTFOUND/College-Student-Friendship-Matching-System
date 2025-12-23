from flask import Blueprint

api_conversation_bp = Blueprint('api_conversation', __name__, url_prefix='/api/conversations')

conversation_bp = Blueprint('conversation', __name__, url_prefix='/conversations')

from . import api
from . import views
